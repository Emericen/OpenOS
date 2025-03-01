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

        self._get_screen_resolution()
        # Socket for receiving input commands
        # self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
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

        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_socket.bind(("0.0.0.0", self.control_port))

    def listen_for_input(self):
        data, addr = self.control_socket.recvfrom(1024)
        message = json.loads(data.decode())

        if message["type"] == "debug":
            print(f"[{addr}]: {message['data']}")

    def stop(self):
        """Stop streaming and close the socket."""
        if self.control_socket:
            self.control_socket.close()
            self.control_socket = None

        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None

    def _handle_input(self):
        """Process incoming input commands."""
        while True:
            data, addr = self.control_socket.recvfrom(1024)
            message = json.loads(data.decode())

            # Set client IP if not already set
            if not self.host_ip:
                self.host_ip = addr[0]
                info_message = json.dumps(
                    {
                        "type": "system_info",
                        "data": {
                            "resolution": self.resolution,
                        },
                    }
                )
                self.control_socket.sendto(info_message.encode(), addr)
                # self._start_stream()

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

    def _get_screen_resolution(self):
        """Get the current screen resolution using xrandr"""
        try:
            output = subprocess.check_output(["xrandr"]).decode("utf-8")
            # Find the current resolution from the output
            for line in output.split("\n"):
                if "*" in line:  # Current resolution has an asterisk
                    resolution = line.split()[0]
                    width, height = map(int, resolution.split("x"))
                    self.resolution = (width, height)
        except:
            # Fallback to default if detection fails
            self.resolution = (1920, 1080)


# Example usage when running inside VM
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
