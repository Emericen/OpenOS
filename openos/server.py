"""
This server runs INSIDE the virtual machine.

It handles two main functions:
1. Streaming the VM's screen to the host machine using ffmpeg
2. Receiving and executing input commands (keyboard/mouse) from the host
"""

import socket
import json
import threading
from pynput import keyboard, mouse
from openos.core.streamer import Streamer


class Server:
    """
    Server component that runs inside the virtual machine.
    It streams the VM's screen to the host and processes input commands.
    This should be installed as a systemd service that starts on VM boot.
    """

    def __init__(self, resolution=(1920, 1080), fps=120, port=8765, control_port=8766):
        self.resolution = resolution
        self.fps = fps
        self.port = port
        self.control_port = control_port
        self.client_ip = None

        # Input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        # Create streamer
        self.streamer = Streamer(resolution=resolution, fps=fps, port=port)

    def set_client_ip(self, ip):
        self.client_ip = ip
        self.streamer.set_client_ip(self.client_ip)

    def start_control_server(self):
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_socket.bind(("0.0.0.0", self.control_port))

        threading.Thread(target=self._handle_control, daemon=True).start()

    def _handle_control(self):
        while True:
            data, addr = self.control_socket.recvfrom(1024)
            message = json.loads(data.decode())

            # Set client IP if not already set
            if not self.client_ip:
                self.client_ip = addr[0]
                self.streamer.set_client_ip(self.client_ip)
                self.streamer.start_stream()

            # Process input commands
            if message["type"] == "keydown":
                self.keyboard_controller.press(message["data"])
            elif message["type"] == "keyup":
                self.keyboard_controller.release(message["data"])
            elif message["type"] == "mousemove":
                self.mouse_controller.position = message["data"]
            elif message["type"] == "mousedown":
                self.mouse_controller.press(message["data"])
            elif message["type"] == "mouseup":
                self.mouse_controller.release(message["data"])

    def start(self):
        """Start the server."""
        self.start_control_server()

    def stop(self):
        """Stop the server and streaming."""
        self.streamer.stop_stream()
        # Note: We're not closing the control socket as it should stay alive
        # until the program exits
