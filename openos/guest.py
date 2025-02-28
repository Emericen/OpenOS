"""
This module runs INSIDE the virtual machine.

It handles two main functions:
1. Streaming the VM's screen to the host machine using ffmpeg
2. Receiving and executing input commands (keyboard/mouse) from the host
"""

import time
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

    def __init__(self, output_port=8765, input_port=8766):
        # Auto-detect resolution
        self.resolution = _get_screen_resolution()
        self.output_port = output_port
        self.input_port = input_port
        self.host_ip = None
        self.ffmpeg_process = None
        self.streaming = False

        # Input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        # Socket for receiving input commands
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def set_host_ip(self, ip):
        """Set the host IP to stream to."""
        self.host_ip = ip

    def start_stream(self):
        """Start streaming the screen using ffmpeg."""
        if not self.host_ip:
            raise ValueError("Host IP not set")

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
            f"udp://{self.host_ip}:{self.output_port}"
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
            if not self.host_ip:
                self.host_ip = addr[0]
                # Send resolution info in first response
                info_message = json.dumps(
                    {"type": "system_info", "data": {"resolution": self.resolution}}
                )
                self.control_socket.sendto(info_message.encode(), addr)
                self.set_host_ip(self.host_ip)
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
        print(
            f"GuestService running. Waiting for client to connect on port {self.input_port}"
        )

    def stop(self):
        """Stop streaming and close the socket."""
        self.stop_stream()
        # Note: We're not closing the control socket here as it should stay alive
        # until the program exits


def _get_screen_resolution():
    """Get the current screen resolution using xrandr"""
    try:
        output = subprocess.check_output(["xrandr"]).decode("utf-8")
        # Find the current resolution from the output
        for line in output.split("\n"):
            if "*" in line:  # Current resolution has an asterisk
                resolution = line.split()[0]
                width, height = map(int, resolution.split("x"))
                return width, height
    except:
        # Fallback to default if detection fails
        return 1920, 1080


# Example usage when running inside VM
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
