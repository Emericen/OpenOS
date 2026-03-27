"""
QMP (QEMU Machine Protocol) client.

Connects to QEMU's QMP socket and provides methods for screenshots,
mouse/keyboard input, and VM lifecycle management.
"""

import json
import socket
import time
from pathlib import Path


class QMPClient:
    """Synchronous QMP client that talks to QEMU over a Unix or TCP socket."""

    def __init__(self, host: str = "localhost", port: int = 4444):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None

    def connect(self, retries: int = 30, delay: float = 2.0):
        """Connect to QMP and negotiate capabilities."""
        for attempt in range(retries):
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(10)
                self._sock.connect((self.host, self.port))
                # Read greeting
                self._read_response()
                # Negotiate capabilities
                self.execute("qmp_capabilities")
                return
            except (ConnectionRefusedError, OSError):
                if self._sock:
                    self._sock.close()
                    self._sock = None
                if attempt < retries - 1:
                    time.sleep(delay)
        raise ConnectionError(
            f"Could not connect to QMP at {self.host}:{self.port} "
            f"after {retries} attempts"
        )

    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    def execute(self, command: str, arguments: dict | None = None) -> dict:
        """Execute a QMP command and return the response."""
        msg = {"execute": command}
        if arguments:
            msg["arguments"] = arguments
        self._send(msg)
        return self._read_response()

    def hmp(self, command_line: str) -> str:
        """Execute an HMP command via QMP and return the output string."""
        resp = self.execute(
            "human-monitor-command",
            {"command-line": command_line},
        )
        return resp.get("return", "")

    # ── High-level commands ──────────────────────────────────────

    def screendump(self, path: str = "/tmp/screen.ppm") -> str:
        """Capture the current screen to a PPM file. Returns the file path."""
        self.execute("screendump", {"filename": path})
        return path

    def mouse_move(self, dx: int, dy: int):
        """Move mouse by relative offset."""
        self.hmp(f"mouse_move {dx} {dy}")

    def mouse_move_abs(self, x: int, y: int):
        """Move mouse to absolute position (requires usb-tablet device)."""
        self.hmp(f"mouse_move {x} {y}")

    def mouse_button(self, state: int):
        """Set mouse button state. 1=left, 2=middle, 4=right. 0=release."""
        self.hmp(f"mouse_button {state}")

    def mouse_click(self, button: int = 1):
        """Click a mouse button (press and release)."""
        self.mouse_button(button)
        time.sleep(0.05)
        self.mouse_button(0)

    def sendkey(self, keys: str, hold_ms: int | None = None):
        """Send key combination. E.g. 'ctrl-alt-delete', 'a', 'ret'."""
        cmd = f"sendkey {keys}"
        if hold_ms is not None:
            cmd += f" {hold_ms}"
        self.hmp(cmd)

    def type_text(self, text: str, delay: float = 0.05):
        """Type a string character by character."""
        key_map = {
            " ": "spc",
            "\n": "ret",
            "\t": "tab",
            "-": "minus",
            "=": "equal",
            "[": "bracket_left",
            "]": "bracket_right",
            "\\": "backslash",
            ";": "semicolon",
            "'": "apostrophe",
            ",": "comma",
            ".": "dot",
            "/": "slash",
            "`": "grave_accent",
        }
        shift_map = {
            "!": "1", "@": "2", "#": "3", "$": "4", "%": "5",
            "^": "6", "&": "7", "*": "8", "(": "9", ")": "0",
            "_": "minus", "+": "equal",
            "{": "bracket_left", "}": "bracket_right",
            "|": "backslash", ":": "semicolon", '"': "apostrophe",
            "<": "comma", ">": "dot", "?": "slash", "~": "grave_accent",
        }
        for ch in text:
            if ch in shift_map:
                self.sendkey(f"shift-{shift_map[ch]}")
            elif ch in key_map:
                self.sendkey(key_map[ch])
            elif ch.isupper():
                self.sendkey(f"shift-{ch.lower()}")
            elif ch.isalnum():
                self.sendkey(ch.lower())
            time.sleep(delay)

    def vm_powerdown(self):
        """Send ACPI shutdown signal."""
        self.execute("system_powerdown")

    def vm_reset(self):
        """Hard reset the VM."""
        self.execute("system_reset")

    def vm_pause(self):
        """Pause the VM."""
        self.execute("stop")

    def vm_resume(self):
        """Resume a paused VM."""
        self.execute("cont")

    def vm_snapshot_save(self, name: str):
        """Save a VM snapshot."""
        self.hmp(f"savevm {name}")

    def vm_snapshot_load(self, name: str):
        """Load a VM snapshot."""
        self.hmp(f"loadvm {name}")

    def vm_snapshot_delete(self, name: str):
        """Delete a VM snapshot."""
        self.hmp(f"delvm {name}")

    def query_status(self) -> dict:
        """Get VM running status."""
        return self.execute("query-status")

    # ── Socket I/O ───────────────────────────────────────────────

    def _send(self, data: dict):
        raw = json.dumps(data).encode() + b"\n"
        self._sock.sendall(raw)

    def _read_response(self) -> dict:
        buf = b""
        while True:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise ConnectionError("QMP connection closed")
            buf += chunk
            try:
                resp = json.loads(buf.decode())
                if "error" in resp:
                    raise RuntimeError(
                        f"QMP error: {resp['error'].get('desc', resp['error'])}"
                    )
                return resp
            except json.JSONDecodeError:
                continue
