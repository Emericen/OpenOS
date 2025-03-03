"""
This module runs INSIDE the virtual machine.

It handles two main functions:
1. Streaming the VM's screen to the host machine using ffmpeg
2. Receiving and executing input commands (keyboard/mouse) from the host
"""

import time
import json
import socket
import subprocess
from pynput import keyboard, mouse


class GuestService:
    """
    Service that runs inside the virtual machine.
    It streams the VM's screen to the host and processes input commands.
    This should be installed as a systemd service that starts on VM boot.
    """

    def __init__(self, video_port=8765, control_port=8766):
        self.host_ip = None
        self.video_port = video_port
        self.control_port = control_port

        self.ffmpeg_process = None
        self.control_socket = None

        # Input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        self.resolution = _get_screen_resolution()

    def start(self):
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_socket.bind(("0.0.0.0", self.control_port))

    def listen_for_input(self):
        data, addr = self.control_socket.recvfrom(1024)
        if self.host_ip and addr[0] != self.host_ip:
            return

        message = json.loads(data.decode())
        if message["type"] == "setup":
            self.host_ip = addr[0]
            self._start_stream()
            print(f"Streaming to host at {self.host_ip}.")
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
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None

    def _start_stream(self):
        # fmt: off
        cmd = [
            "ffmpeg", "-f", "x11grab", 
            "-video_size", f"{self.resolution[0]}x{self.resolution[1]}", 
            "-framerate", "120", 
            "-i", ":0.0", 
            "-vcodec", "libx264", 
            "-preset", "ultrafast", 
            "-f", "mpegts", 
            "-tune", "zerolatency", 
            f"udp://{self.host_ip}:{self.video_port}"
        ]
        # fmt: on
        self.ffmpeg_process = subprocess.Popen(cmd)


def _get_screen_resolution():
    """Get the current screen resolution using xrandr"""
    try:
        output = subprocess.check_output(["xrandr"]).decode("utf-8")
        # Find the current resolution from the output
        for line in output.split("\n"):
            if "*" in line:  # Current resolution has an asterisk
                resolution = line.split()[0]
                width, height = map(int, resolution.split("x"))
                return (width, height)
    except:
        # Fallback to default if detection fails
        return (1920, 1080)


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
