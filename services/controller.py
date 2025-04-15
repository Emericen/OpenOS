import json
import socket
from datetime import datetime
from services.log_setup import setup_logging
from services.constants import (
    KEY_MAPPING,
    MOUSE_BUTTON_MAPPING,
    SCROLL_MAPPING,
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

    def handle_mouse_move(self, x, y):
        x, y = int(x), int(y)
        if not 0 <= x <= 32767 or not 0 <= y <= 32767:
            return False, f"Mouse coordinates out of range: {x}, {y}"

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
        return True, None

    def handle_mouse_down(self, button):
        if button not in MOUSE_BUTTON_MAPPING:
            return False, f"Invalid mouse button: {button}"

        qemu_button = MOUSE_BUTTON_MAPPING[button]

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {"type": "btn", "data": {"down": True, "button": qemu_button}}
                    ]
                },
            }
        )
        return True, None

    def handle_mouse_up(self, button):
        if button not in MOUSE_BUTTON_MAPPING:
            return False, f"Invalid mouse button: {button}"

        qemu_button = MOUSE_BUTTON_MAPPING[button]

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {"type": "btn", "data": {"down": False, "button": qemu_button}}
                    ]
                },
            }
        )
        return True, None

    def handle_scroll(self, direction):
        if direction not in SCROLL_MAPPING:
            return False, f"Invalid scroll direction: {direction}"

        qemu_button = SCROLL_MAPPING[direction]

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [{"type": "btn", "data": {"down": True, "button": qemu_button}}]
                },
            }
        )
        return True, None

    def handle_key_down(self, key):
        if key not in KEY_MAPPING:
            return False, f"Invalid key: {key}"

        qemu_key = KEY_MAPPING[key]

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {
                            "type": "key",
                            "data": {
                                "down": True,
                                "key": {"type": "qcode", "data": qemu_key},
                            },
                        }
                    ]
                },
            }
        )
        return True, None

    def handle_key_up(self, key):
        if key not in KEY_MAPPING:
            return False, f"Invalid key: {key}"

        qemu_key = KEY_MAPPING[key]

        _ = self._send_to_qmp_socket(
            {
                "execute": "input-send-event",
                "arguments": {
                    "events": [
                        {
                            "type": "key",
                            "data": {
                                "down": False,
                                "key": {"type": "qcode", "data": qemu_key},
                            },
                        }
                    ]
                },
            }
        )
        return True, None

    def handle_screenshot(self, filename=None, file_format="png"):
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
        return True, None

    def _send_to_qmp_socket(self, data: dict) -> dict:
        self.qmp_socket.sendall(json.dumps(data).encode() + b"\n")
        response = self.qmp_socket.recv(1024).decode()
        return response
