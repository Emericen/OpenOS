"""
OpenOS Python SDK.

A simple client for AI agents to control a desktop VM via the OpenOS API.

Usage:
    from openos import Desktop

    desktop = Desktop("http://localhost:8100")
    screenshot = desktop.screenshot()       # PIL Image
    desktop.click(500, 300)                 # click at (x, y)
    desktop.type_text("hello world")        # type text
    desktop.key("ctrl-s")                   # key combo
"""

import io
from dataclasses import dataclass

import requests
from PIL import Image


@dataclass
class Desktop:
    """Client for controlling an OpenOS desktop VM."""

    base_url: str = "http://localhost:8100"
    timeout: float = 30.0

    def _post(self, path: str, json: dict | None = None) -> dict:
        resp = requests.post(
            f"{self.base_url}{path}", json=json, timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str) -> requests.Response:
        resp = requests.get(f"{self.base_url}{path}", timeout=self.timeout)
        resp.raise_for_status()
        return resp

    # ── Screenshot ───────────────────────────────────────────────

    def screenshot(self) -> Image.Image:
        """Capture the current screen. Returns a PIL Image."""
        resp = self._get("/screenshot")
        return Image.open(io.BytesIO(resp.content))

    # ── Mouse ────────────────────────────────────────────────────

    def move(self, x: int, y: int):
        """Move the mouse to absolute position (x, y)."""
        self._post("/mouse/move", {"x": x, "y": y})

    def click(self, x: int, y: int, button: int = 1):
        """Move to (x, y) and click. 1=left, 2=middle, 4=right."""
        self.move(x, y)
        self._post("/mouse/click", {"button": button})

    def right_click(self, x: int, y: int):
        """Right-click at (x, y)."""
        self.click(x, y, button=4)

    def double_click(self, x: int, y: int):
        """Double-click at (x, y)."""
        self.click(x, y)
        self.click(x, y)

    # ── Keyboard ─────────────────────────────────────────────────

    def key(self, keys: str, hold_ms: int | None = None):
        """Send a key combination. E.g. 'ctrl-alt-delete', 'ret', 'a'."""
        payload = {"keys": keys}
        if hold_ms is not None:
            payload["hold_ms"] = hold_ms
        self._post("/keyboard/key", payload)

    def type_text(self, text: str, delay: float = 0.05):
        """Type a string character by character."""
        self._post("/keyboard/type", {"text": text, "delay": delay})

    # ── VM Lifecycle ─────────────────────────────────────────────

    def status(self) -> dict:
        """Get VM running status."""
        return self._get("/vm/status").json()

    def pause(self):
        """Pause the VM."""
        self._post("/vm/pause")

    def resume(self):
        """Resume a paused VM."""
        self._post("/vm/resume")

    def reset(self):
        """Hard reset the VM."""
        self._post("/vm/reset")

    def powerdown(self):
        """Send ACPI shutdown."""
        self._post("/vm/powerdown")

    def snapshot_save(self, name: str):
        """Save a VM snapshot."""
        self._post("/vm/snapshot/save", {"name": name})

    def snapshot_load(self, name: str):
        """Load a VM snapshot."""
        self._post("/vm/snapshot/load", {"name": name})

    def snapshot_delete(self, name: str):
        """Delete a VM snapshot."""
        self._post("/vm/snapshot/delete", {"name": name})
