import json
import time
import threading
from mss import mss
import numpy as np
from pynput import keyboard, mouse
import os


class GuestService:
    """
    This module runs INSIDE the virtual machine.

    It handles two main functions:
        1. Streaming the VM's screen to the host machine.
        2. Receiving and executing input commands (keyboard & mouse etc.) from the host
    """

    def __init__(self):
        # Input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        self._shared_folder_path = "/mnt/hgfs/temp"

        # Make sure file names match what the host is using
        frame_buffer_path = f"{self._shared_folder_path}/frame_buffer.dat"

        # Create the file if it doesn't exist
        if not os.path.exists(frame_buffer_path):
            empty_buffer = np.zeros((720, 1280, 4), dtype=np.uint8)
            empty_buffer.tofile(frame_buffer_path)

        # Video "streaming"
        self._frame_buffer = np.memmap(
            filename=frame_buffer_path,
            dtype=np.uint8,
            mode="r+",
            shape=(720, 1280, 4),  # TODO: get using xrandr
        )

        # Control buffer
        self._control_buffer = []
        self._control_buffer_path = f"{self._shared_folder_path}/control_buffer.json"

    def start(self):
        self._main_loop_thread = threading.Thread(target=self._main_loop)
        self._main_loop_thread.start()

    def _main_loop(self):
        with mss() as sct:
            while True:
                frame = sct.grab(sct.monitors[1])
                frame = np.array(frame)
                self._frame_buffer[:] = frame[:]
                self._frame_buffer.flush()

                self._read_from_buffer()

    def stop(self):
        """Stop streaming and close the socket."""
        if self._main_loop_thread:
            self._main_loop_thread.join()
            self._main_loop_thread = None
        if self._frame_buffer:
            self._frame_buffer._mmap.close()
            self._frame_buffer = None

    def _read_from_buffer(self):
        # Only process if there are messages
        if self._control_buffer and len(self._control_buffer) > 0:
            message = self._control_buffer[-1]

            if message["role"] == "host":
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
                else:
                    print(f"Unknown message type: {message['type']}")

    def _get_button_from_str(self, button_str):
        """Get the button from the string"""
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


if __name__ == "__main__":
    service = GuestService()
    service.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
        print("GuestService stopped")
