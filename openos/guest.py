import json
import socket
import subprocess
from mss import mss
import numpy as np
from pynput import keyboard, mouse
import os
from openos.utils import PASSWORD


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
        print(f"Received message from {addr}: {message}")

        if message["type"] == "move_mouse":
            dx, dy = message["data"]["dx"], message["data"]["dy"]
            self.mouse_controller.move(dx, dy)
        elif message["type"] == "position_mouse":
            x, y = message["data"]["x"], message["data"]["y"]
            self.mouse_controller.position = (x, y)
        elif message["type"] == "button_down":
            button_str = self._get_button_from_str(message["data"]["button"])
            self.mouse_controller.press(button_str)
        elif message["type"] == "button_up":
            button_str = self._get_button_from_str(message["data"]["button"])
            self.mouse_controller.release(button_str)
        elif message["type"] == "scroll":
            dx, dy = message["data"]["dx"], message["data"]["dy"]
            self.mouse_controller.scroll(dx, dy)
        elif message["type"] == "key_down":
            key_str = self._get_key_from_str(message["data"]["key"])
            self.keyboard_controller.press(key_str)
        elif message["type"] == "key_up":
            key_str = self._get_key_from_str(message["data"]["key"])
            self.keyboard_controller.release(key_str)
        elif message["type"] == "stop":
            self.terminate()
            return False
        else:
            print(f"[{addr}]: {message['data']}")
        return True

    def terminate(self):
        if self._frame_buffer:
            self._frame_buffer._mmap.close()
            self._frame_buffer = None
        self.control_socket.close()

    def _get_button_from_str(self, button_str):
        if button_str == "mouse.Button.left":
            return mouse.Button.left
        elif button_str == "mouse.Button.right":
            return mouse.Button.right
        elif button_str == "mouse.Button.middle":
            return mouse.Button.middle
        return button_str

    def _get_key_from_str(self, key_str):
        if key_str.startswith("Key."):
            key_name = key_str.split(".")[1]
            return getattr(keyboard.Key, key_name)
        return key_str

    def _allow_udp_on_port(self, port: int):
        # Set up firewall rules
        try:
            print("Setting up firewall rules...")
            subprocess.run(
                ["sudo", "-S", "ufw", "allow", f"{port}/udp"],
                input=PASSWORD.encode(),
                check=True,
            )
        except Exception as e:
            print(f"Failed to set up firewall: {e}")


if __name__ == "__main__":
    with mss() as sct:
        service = GuestService(sct)
        try:
            running = True
            while running:
                running = service.update()
        except KeyboardInterrupt:
            service.terminate()
            print("GuestService stopped")
