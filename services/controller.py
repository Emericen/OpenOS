import json
import socket
from datetime import datetime
from services.log_setup import setup_logging
from services.constants import (
    VALID_QEMU_KEYS,
    VALID_QEMU_MOUSE_BUTTONS,
    VALID_QEMU_MOUSE_SCROLL_BUTTONS,
)

logging = setup_logging()

"""
QEMU Machine Protocol (QMP)

    General Documentation:    
        https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html

    Input send event: 
        https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#command-QMP-ui.input-send-event

    Screendump:
        https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#command-QMP-ui.screendump
"""


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
            "mouse_position": self.mouse_position,
            "mouse_scroll": self.mouse_scroll,
            "keyboard_key_down": self.keyboard_key_down,
            "keyboard_key_up": self.keyboard_key_up,
            "screenshot": self.screenshot,
        }

    def mouse_btn_down(self, btn: str):
        if not btn in VALID_QEMU_MOUSE_BUTTONS:
            return

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [{"type": "btn", "data": {"down": True, "button": btn}}]
                },
            }
        )

    def mouse_btn_up(self, btn: str):
        if not btn in VALID_QEMU_MOUSE_BUTTONS:
            return

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [{"type": "btn", "data": {"down": False, "button": btn}}]
                },
            }
        )

    def mouse_position(self, x: int, y: int):
        if not 0 <= x <= 32767 or not 0 <= y <= 32767:
            return

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

    def mouse_scroll(self, btn: str):
        if not btn in VALID_QEMU_MOUSE_SCROLL_BUTTONS:
            return

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [{"type": "btn", "data": {"down": True, "button": btn}}]
                },
            }
        )

    def keyboard_key_down(self, key: str):
        if not key in VALID_QEMU_KEYS:
            return

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {
                            "type": "key",
                            "data": {
                                "down": True,
                                "key": {"type": "qcode", "data": key},
                            },
                        }
                    ]
                },
            }
        )

    def keyboard_key_up(self, key: str):
        if not key in VALID_QEMU_KEYS:
            return

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {
                            "type": "key",
                            "data": {
                                "down": False,
                                "key": {"type": "qcode", "data": key},
                            },
                        }
                    ]
                },
            }
        )

    def screenshot(self, filename: str = None, file_format: str = "png"):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"screenshot_{timestamp}.{file_format}"

        if not filename.startswith("/shared/"):
            filename = f"/shared/{filename}"

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
