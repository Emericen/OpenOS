"""
This module runs INSIDE the virtual machine.

It handles two main functions:
1. Streaming the VM's screen to the host machine using ffmpeg
2. Receiving and executing input commands (keyboard/mouse) from the host
"""

import socket
import json
import threading
import subprocess
from pynput import keyboard, mouse


class GuestService:
    """
    Service that runs inside the virtual machine.
    It streams the VM's screen to the host and processes input commands.
    This should be installed as a systemd service that starts on VM boot.
    """

    def __init__(self, resolution=(1920, 1080), fps=120, output_port=8765, input_port=8766):
        self.resolution = resolution
        self.fps = fps
        self.output_port = output_port
        self.input_port = input_port
        self.client_ip = None
        self.ffmpeg_process = None
        self.streaming = False

        # Input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        # Socket for receiving input commands
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def set_client_ip(self, ip):
        """Set the client IP to stream to."""
        self.client_ip = ip

    def start_stream(self):
        """Start streaming the screen using ffmpeg."""
        if not self.client_ip:
            raise ValueError("Client IP not set")

        # fmt: off
        cmd = [
            "ffmpeg", "-f", "x11grab", 
            "-video_size", f"{self.resolution[0]}x{self.resolution[1]}", 
            "-framerate", str(self.fps), 
            "-i", ":0.0", 
            "-vcodec", "libx264", 
            "-preset", "ultrafast", 
            "-f", "mpegts", 
            "-tune", "zerolatency", 
            f"udp://{self.client_ip}:{self.output_port}"
        ]
        # fmt: on

        self.ffmpeg_process = subprocess.Popen(cmd)
        self.streaming = True

    def stop_stream(self):
        """Stop the ffmpeg stream."""
        if self.streaming and self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.streaming = False

    def start_input_server(self):
        """Start the UDP server for receiving input commands."""
        self.control_socket.bind(("0.0.0.0", self.input_port))
        threading.Thread(target=self._handle_input, daemon=True).start()

    def _handle_input(self):
        """Process incoming input commands."""
        while True:
            data, addr = self.control_socket.recvfrom(1024)
            message = json.loads(data.decode())

            # Set client IP if not already set
            if not self.client_ip:
                self.client_ip = addr[0]
                self.set_client_ip(self.client_ip)
                self.start_stream()

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
        """Start both the input server and streaming (when client connects)."""
        self.start_input_server()
        print(f"GuestService running. Waiting for client to connect on port {self.input_port}")
        
    def stop(self):
        """Stop streaming and close the socket."""
        self.stop_stream()
        # Note: We're not closing the control socket here as it should stay alive
        # until the program exits

# Example usage when running inside VM
if __name__ == "__main__":
    service = GuestService()
    service.start()
    
    # Keep the main thread alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
        print("GuestService stopped")
