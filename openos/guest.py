import json
import socket
import subprocess
import numpy as np
import mss
import threading
from pynput import keyboard, mouse
from utils import PASSWORD


class GuestService:
    """
    This module runs INSIDE the virtual machine.

    It handles two main functions:
        1. Streaming the VM's screen to the host machine.
        2. Receiving and executing input commands (keyboard & mouse etc.) from the host
    """

    def __init__(self, control_port=8765):
        self.host_ip = None
        self.control_port = control_port
        self.control_socket = None
        _allow_udp_on_port(control_port)

        # Input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        # Video "streaming"
        self._frame_buffer = np.memmap(
            filename="/mnt/hgfs/temp/frame.dat",
            # NOTE: ^ this is guest's shared folder with host
            dtype=np.uint8,
            mode="w+",
            shape=(1280, 720, 3),
            # NOTE: ^ resolution hardcoded for now. can use xrandr to obtain.
        )

    def start(self):
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_socket.bind(("0.0.0.0", self.control_port))
        self._stream_thread = threading.Thread(target=self._start_stream)
        self._stream_thread.start()

    def _start_stream(self):
        with mss() as sct:
            while True:
                frame = sct.grab(sct.monitors[1])
                frame = np.array(frame)
                self._frame_buffer[:] = frame[:]
                self._frame_buffer.flush()

    def listen_for_input(self):
        data, addr = self.control_socket.recvfrom(1024)
        message = json.loads(data.decode())
        print(f"Received message from {addr}: {message}")

        if message["type"] == "start_stream":
            self.host_ip = addr[0]
            self._start_stream()
        elif message["type"] == "move_mouse":
            dx, dy = message["data"]["dx"], message["data"]["dy"]
            self.mouse_controller.move(dx, dy)
        elif message["type"] == "position_mouse":
            x, y = message["data"]["x"], message["data"]["y"]
            self.mouse_controller.position = (x, y)
        elif message["type"] == "button_down":
            button_str = _get_button_from_str(message["data"]["button"])
            self.mouse_controller.press(button_str)
        elif message["type"] == "button_up":
            button_str = _get_button_from_str(message["data"]["button"])
            self.mouse_controller.release(button_str)
        elif message["type"] == "scroll":
            dx, dy = message["data"]["dx"], message["data"]["dy"]
            self.mouse_controller.scroll(dx, dy)
        elif message["type"] == "key_down":
            key_str = _get_key_from_str(message["data"]["key"])
            self.keyboard_controller.press(key_str)
        elif message["type"] == "key_up":
            key_str = _get_key_from_str(message["data"]["key"])
            self.keyboard_controller.release(key_str)
        else:
            print(f"[{addr}]: {message['data']}")

    def stop(self):
        """Stop streaming and close the socket."""
        if self.control_socket:
            self.control_socket.close()
            self.control_socket = None
        if self._stream_thread:
            self._stream_thread.join()
            self._stream_thread = None
        if self._frame_buffer:
            self._frame_buffer._mmap.close()
            self._frame_buffer = None


def _allow_udp_on_port(port: int):
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


def _get_button_from_str(button_str):
    """Get the button from the string"""
    if button_str == "mouse.Button.left":
        return mouse.Button.left
    elif button_str == "mouse.Button.right":
        return mouse.Button.right
    elif button_str == "mouse.Button.middle":
        return mouse.Button.middle
    return button_str


def _get_key_from_str(key_str):
    if key_str.startswith("Key."):
        key_name = key_str.split(".")[1]
        return getattr(keyboard.Key, key_name)
    return key_str


if __name__ == "__main__":
    service = GuestService()
    service.start()

    # Keep the main thread alive
    try:
        while True:
            service.listen_for_input()
    except KeyboardInterrupt:
        service.stop()
        print("GuestService stopped")
