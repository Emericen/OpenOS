import json
import socket
from datetime import datetime
from services.log_setup import setup_logging
from services.constants import VALID_QEMU_KEYS

logging = setup_logging()


class Controller:
    def __init__(self):
        # Connect to QEMU Machine Protocol (QMP) socket
        self.qmp_host, self.qmp_port = "localhost", 4444
        self.qmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.qmp_socket.connect((self.qmp_host, self.qmp_port))
        response = self._send_to_qmp_socket({"execute": "qmp_capabilities"})
        logging.info(f"QMP connected to {self.qmp_host}:{self.qmp_port}")
        logging.info(f"QMP capabilities: {response}")

        # Map out all available actions
        self.actions = {
            "mouse_btn_down": self.mouse_btn_down,
            "mouse_btn_up": self.mouse_btn_up,
            "mouse_move": self.mouse_move,
            "mouse_position": self.mouse_position,
            "mouse_scroll": self.mouse_scroll,
            "keyboard_key_down": self.keyboard_key_down,
            "keyboard_key_up": self.keyboard_key_up,
            "screenshot": self.screenshot,
        }

    def mouse_btn_down(self, btn: str):
        """
        Reference: https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#command-QMP-ui.input-send-event
        """
        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [{"type": "btn", "data": {"down": True, "button": btn}}]
                },
            }
        )

    def mouse_btn_up(self, btn: str):
        """
        Reference: https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#command-QMP-ui.input-send-event
        """
        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [{"type": "btn", "data": {"down": False, "button": btn}}]
                },
            }
        )

    def mouse_move(self, x: int, y: int):
        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {"type": "abs", "data": {"axis": "x", "value": x}},
                        {"type": "abs", "data": {"axis": "y", "value": y}},
                    ]
                },
            }
        )

    def mouse_position(self, x: int, y: int):
        """
        Move mouse to absolute position

        Reference: https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#command-QMP-ui.input-send-event
        """

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {"type": "abs", "data": {"axis": "x", "value": x}},
                        {"type": "abs", "data": {"axis": "y", "value": y}},
                    ]
                },
            }
        )

    def mouse_scroll_up(self):
        """
        Reference: https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#enum-QMP-ui.InputButton
        """
        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {"type": "btn", "data": {"down": True, "button": "wheel-up"}}
                    ]
                },
            }
        )

    def mouse_scroll_down(self):
        """
        Reference: https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#enum-QMP-ui.InputButton
        """
        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {"type": "btn", "data": {"down": True, "button": "wheel-down"}}
                    ]
                },
            }
        )

    def keyboard_key_down(self, key: str):
        """
        Reference: https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#command-QMP-ui.input-send-event
        """
        if not key in VALID_QEMU_KEYS:
            return

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {
                            "type": "key",
                            "data": {"down": True, "type": "qcode", "data": key},
                        }
                    ]
                },
            }
        )

    def keyboard_key_up(self, key: str):
        """
        Reference: https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#command-QMP-ui.input-send-event
        """
        if not key in VALID_QEMU_KEYS:
            return

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {
                            "type": "key",
                            "data": {"down": False, "type": "qcode", "data": key},
                        }
                    ]
                },
            }
        )

    def screenshot(self, filename: str = None, file_format: str = "png"):
        """
        Reference: https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#command-QMP-ui.screendump
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"/shared/screenshot_{timestamp}.{file_format}"

        _ = self._send_to_qmp_socket(
            {
                "execute": "screendump",
                "arguments": {"filename": filename, "format": file_format},
            }
        )

    def _send_to_qmp_socket(self, data: dict) -> dict:
        self.qmp_socket.sendall(json.dumps(data).encode() + b"\n")
        response = self.qmp_socket.recv(1024).decode()
        logging.debug(f"QMP {data} response: {response}")
        return response
