import os
import json
import socket
import subprocess
import logging
from mss import mss
import numpy as np
from pynput import keyboard, mouse
from openos.utils import PASSWORD

logger = logging.getLogger(__name__)


KEYBOARD_MAPPING = [
    ("ESC", keyboard.Key.esc),
    ("ENTER", keyboard.Key.enter),
    ("BACKSPACE", keyboard.Key.backspace),
    ("TAB", keyboard.Key.tab),
    ("SPACE", keyboard.Key.space),
    ("LEFT", keyboard.Key.left),
    ("RIGHT", keyboard.Key.right),
    ("UP", keyboard.Key.up),
    ("DOWN", keyboard.Key.down),
    ("A", keyboard.KeyCode.from_char("a")),
    ("B", keyboard.KeyCode.from_char("b")),
    ("C", keyboard.KeyCode.from_char("c")),
    ("D", keyboard.KeyCode.from_char("d")),
    ("E", keyboard.KeyCode.from_char("e")),
    ("F", keyboard.KeyCode.from_char("f")),
    ("G", keyboard.KeyCode.from_char("g")),
    ("H", keyboard.KeyCode.from_char("h")),
    ("I", keyboard.KeyCode.from_char("i")),
    ("J", keyboard.KeyCode.from_char("j")),
    ("K", keyboard.KeyCode.from_char("k")),
    ("L", keyboard.KeyCode.from_char("l")),
    ("M", keyboard.KeyCode.from_char("m")),
    ("N", keyboard.KeyCode.from_char("n")),
    ("O", keyboard.KeyCode.from_char("o")),
    ("P", keyboard.KeyCode.from_char("p")),
    ("Q", keyboard.KeyCode.from_char("q")),
    ("R", keyboard.KeyCode.from_char("r")),
    ("S", keyboard.KeyCode.from_char("s")),
    ("T", keyboard.KeyCode.from_char("t")),
    ("U", keyboard.KeyCode.from_char("u")),
    ("V", keyboard.KeyCode.from_char("v")),
    ("W", keyboard.KeyCode.from_char("w")),
    ("X", keyboard.KeyCode.from_char("x")),
    ("Y", keyboard.KeyCode.from_char("y")),
    ("Z", keyboard.KeyCode.from_char("z")),
    ("0", keyboard.KeyCode.from_char("0")),
    ("1", keyboard.KeyCode.from_char("1")),
    ("2", keyboard.KeyCode.from_char("2")),
    ("3", keyboard.KeyCode.from_char("3")),
    ("4", keyboard.KeyCode.from_char("4")),
    ("5", keyboard.KeyCode.from_char("5")),
    ("6", keyboard.KeyCode.from_char("6")),
    ("7", keyboard.KeyCode.from_char("7")),
    ("8", keyboard.KeyCode.from_char("8")),
    ("9", keyboard.KeyCode.from_char("9")),
    ("F1", keyboard.Key.f1),
    ("F2", keyboard.Key.f2),
    ("F3", keyboard.Key.f3),
    ("F4", keyboard.Key.f4),
    ("F5", keyboard.Key.f5),
    ("F6", keyboard.Key.f6),
    ("F7", keyboard.Key.f7),
    ("F8", keyboard.Key.f8),
    ("F9", keyboard.Key.f9),
    ("F10", keyboard.Key.f10),
    ("F11", keyboard.Key.f11),
    ("F12", keyboard.Key.f12),
    ("[", keyboard.KeyCode.from_char("[")),
    ("]", keyboard.KeyCode.from_char("]")),
    ("\\", keyboard.KeyCode.from_char("\\")),
    (";", keyboard.KeyCode.from_char(";")),
    ("'", keyboard.KeyCode.from_char("'")),
    (",", keyboard.KeyCode.from_char(",")),
    (".", keyboard.KeyCode.from_char(".")),
    ("/", keyboard.KeyCode.from_char("/")),
    ("`", keyboard.KeyCode.from_char("`")),
    ("(", keyboard.KeyCode.from_char("(")),
    (")", keyboard.KeyCode.from_char(")")),
    ("{", keyboard.KeyCode.from_char("{")),
    ("}", keyboard.KeyCode.from_char("}")),
    ("=", keyboard.KeyCode.from_char("=")),
    ("-", keyboard.KeyCode.from_char("-")),
    ("_", keyboard.KeyCode.from_char("_")),
    ("+", keyboard.KeyCode.from_char("+")),
    ("*", keyboard.KeyCode.from_char("*")),
    ("#", keyboard.KeyCode.from_char("#")),
    ("%", keyboard.KeyCode.from_char("%")),
    ("CAPSLOCK", keyboard.Key.caps_lock),
    ("DELETE", keyboard.Key.delete),
    ("HOME", keyboard.Key.home),
    ("END", keyboard.Key.end),
    ("PAGEUP", keyboard.Key.page_up),
    ("PAGEDOWN", keyboard.Key.page_down),
    ("LEFT_CTRL", keyboard.Key.ctrl_l),
    ("RIGHT_CTRL", keyboard.Key.ctrl_r),
    ("LEFT_SHIFT", keyboard.Key.shift_l),
    ("RIGHT_SHIFT", keyboard.Key.shift_r),
    ("LEFT_ALT", keyboard.Key.alt_l),
    ("RIGHT_ALT", keyboard.Key.alt_r),
    ("LEFT_CMD", keyboard.Key.cmd_l),
    ("RIGHT_CMD", keyboard.Key.cmd_r),
]
KEYBOARD_NAME_TO_KEY = {key[0]: key[1] for key in KEYBOARD_MAPPING}
KEYBOARD_KEY_TO_NAME = {key[1]: key[0] for key in KEYBOARD_MAPPING}

MOUSE_MAPPING = [
    ("LEFT", mouse.Button.left),
    ("RIGHT", mouse.Button.right),
    ("MIDDLE", mouse.Button.middle),
]
MOUSE_NAME_TO_BUTTON = {button[0]: button[1] for button in MOUSE_MAPPING}
MOUSE_BUTTON_TO_NAME = {button[1]: button[0] for button in MOUSE_MAPPING}


class GuestService:
    """
    This module runs INSIDE the virtual machine.

    It handles two main functions:
        1. Updating the frame buffer with the VM's screen.
        2. Receiving and executing input commands (keyboard & mouse etc.) from the host
    """

    def __init__(self, sct: mss, control_port: int = 8765):
        # Screen capture tool (mss instance) for grabbing VM's display
        self.sct = sct

        # Shared frame buffer
        frame_buffer_path = "/mnt/hgfs/temp/frame_buffer.dat"
        if not os.path.exists(frame_buffer_path):
            empty_buffer = np.zeros((720, 1280, 4), dtype=np.uint8)
            empty_buffer.tofile(frame_buffer_path)
        self._frame_buffer = np.memmap(
            filename=frame_buffer_path,
            dtype=np.uint8,
            mode="r+",
            shape=(720, 1280, 4),  # TODO: get using xrandr
        )

        # Control socket
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_socket.bind(("0.0.0.0", control_port))
        self._allow_udp_on_port(control_port)

        # Input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

    def update(self):
        frame = self.sct.grab(self.sct.monitors[1])
        frame = np.array(frame)
        self._frame_buffer[:] = frame[:]
        self._frame_buffer.flush()
        return self._listen_for_control()

    def _listen_for_control(self) -> bool:
        data, addr = self.control_socket.recvfrom(1024)
        message = json.loads(data.decode())
        logger.info(f"Received command from {addr}: {message['data']}")

        if message["type"] == "move_mouse":
            dx, dy = message["data"]["dx"], message["data"]["dy"]
            self.mouse_controller.move(dx, dy)
        elif message["type"] == "position_mouse":
            x, y = message["data"]["x"], message["data"]["y"]
            self.mouse_controller.position = (x, y)
        elif message["type"] == "button_down":
            button_str = message["data"]["button"]
            button = MOUSE_NAME_TO_BUTTON[button_str]
            self.mouse_controller.press(button)
        elif message["type"] == "button_up":
            button_str = message["data"]["button"]
            button = MOUSE_NAME_TO_BUTTON[button_str]
            self.mouse_controller.release(button)
        elif message["type"] == "scroll":
            dx, dy = message["data"]["dx"], message["data"]["dy"]
            self.mouse_controller.scroll(dx, dy)
        elif message["type"] == "key_down":
            key_str = message["data"]["key"]
            key = KEYBOARD_NAME_TO_KEY[key_str]
            self.keyboard_controller.press(key)
        elif message["type"] == "key_up":
            key_str = message["data"]["key"]
            key = KEYBOARD_NAME_TO_KEY[key_str]
            self.keyboard_controller.release(key)
        elif message["type"] == "stop":
            self.terminate()
            return False

        return True

    def terminate(self):
        if self._frame_buffer:
            self._frame_buffer._mmap.close()
            self._frame_buffer = None
        self.control_socket.close()
        logger.info("GuestService terminated")

    def _allow_udp_on_port(self, port: int):
        try:
            logger.info(f"Setting up firewall rules for port {port}/udp...")
            subprocess.run(
                ["sudo", "-S", "ufw", "allow", f"{port}/udp"],
                input=PASSWORD.encode(),
                check=True,
            )
        except Exception as e:
            logger.error(f"Failed to set up firewall: {e}")


if __name__ == "__main__":
    logger.info("Starting GuestService...")
    with mss(with_cursor=True) as sct:
        service = GuestService(sct)
        try:
            running = True
            logger.info("GuestService initialized and running")
            while running:
                running = service.update()
        except KeyboardInterrupt:
            service.terminate()
            logger.info("GuestService stopped by keyboard interrupt")
