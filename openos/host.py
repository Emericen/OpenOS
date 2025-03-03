import os
import re
import time
import json
import socket
import subprocess
import numpy as np

from openos.utils import install_ubuntu
from openos.utils import (
    USER,
    PASSWORD,
    GUEST_OUTPUT_FILE,
    HOST_OUTPUT_FILE,
)

START_WAIT_TIME = 10  # seconds


class HostService:
    """Manages the virtual machine and communication with the VM server."""

    def __init__(self, video_port: int = 8765, control_port: int = 8766):
        self.guest_ip = None
        self.video_port = video_port
        self.control_port = control_port

        self.ffmpeg_process = None
        self.control_socket = None

        self.vm_path = install_ubuntu()
        self.resolution = None

    def start(self):
        # Start the guest
        subprocess.run(["vmrun", "start", self.vm_path])
        self._wait_for_ip_address()

        # Start the guest service
        cmd = ["cd ~/OpenOS", "python guest.py"]
        _ = self._execute_commands_in_guest(cmd)

        # Get the resolution of the guest
        cmd = ["DISPLAY=:0 xdpyinfo | grep dimensions"]
        output_str = self._execute_commands_in_guest(cmd)
        self.resolution = self._parse_resolution(output_str)

        # Set up the control socket
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._send_data({"type": "setup", "data": {}})

        # fmt: off
        cmd = [
            "ffmpeg", "-fflags", "nobuffer", 
            "-f", "mpegts", 
            "-i", f"udp://{self.guest_ip}:{self.video_port}", 
            "-f", "rawvideo", 
            "-flags", "low_delay", 
            "-avioflags", "direct", 
            "-pix_fmt", "rgb24", 
            "-vf", "format=rgb24", 
            "pipe:1"
        ]
        # fmt: on
        self.ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    def stop(self):
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None
        if self.control_socket:
            self.control_socket.close()
        subprocess.run(["vmrun", "stop", self.vm_path])

    def reset(self):
        subprocess.run(["vmrun", "reset", self.vm_path])

    def save(self, snapshot_name="snapshot"):
        subprocess.run(["vmrun", "saveSnapshot", self.vm_path, snapshot_name])

    def load(self, snapshot_name="snapshot"):
        subprocess.run(["vmrun", "loadSnapshot", self.vm_path, snapshot_name])

    def move_mouse(self, dx, dy):
        self._send_data({"type": "move_mouse", "data": {"dx": dx, "dy": dy}})

    def button_down(self, button):
        self._send_data({"type": "button_down", "data": {"button": button}})

    def button_up(self, button):
        self._send_data({"type": "button_up", "data": {"button": button}})

    def scroll(self, dx, dy):
        self._send_data({"type": "scroll", "data": {"dx": dx, "dy": dy}})

    def key_down(self, key):
        self._send_data({"type": "key_down", "data": {"key": key}})

    def key_up(self, key):
        self._send_data({"type": "key_up", "data": {"key": key}})

    def _send_data(self, data: dict):
        if not self.guest_ip:
            raise ValueError("VM not started or IP address not available")
        data = json.dumps(data)
        self.control_socket.sendto(data.encode(), (self.guest_ip, self.control_port))

    def _execute_commands_in_guest(self, commands: list[str]):
        result = None
        # Run commands in guest and save output to file
        combined = " && ".join(commands)
        cmd = f'vmrun -T ws -gu {USER} -gp {PASSWORD} runProgramInGuest "{self.vm_path}" /bin/bash -c "{combined} > {GUEST_OUTPUT_FILE} 2>&1'
        subprocess.run(cmd, shell=True)

        # Copy output file from guest to host
        copy_cmd = f'vmrun -T ws -gu {USER} -gp {PASSWORD} copyFileFromGuestToHost "{self.vm_path}" "{GUEST_OUTPUT_FILE}" "{HOST_OUTPUT_FILE}"'
        subprocess.run(copy_cmd, shell=True)

        # Delete output file from guest
        delete_cmd = f'vmrun -T ws -gu {USER} -gp {PASSWORD} runProgramInGuest "{self.vm_path}" /bin/bash -c "rm {GUEST_OUTPUT_FILE}"'
        subprocess.run(delete_cmd, shell=True)

        # Read output file in host
        with open(HOST_OUTPUT_FILE, "r") as file:
            result = file.read()

        # Delete output file in host
        os.remove(HOST_OUTPUT_FILE)
        return result

    def _wait_for_ip_address(self):
        while True:
            try:
                ip_address = subprocess.run(
                    ["vmrun", "getGuestIPAddress", self.vm_path],
                    capture_output=True,
                    text=True,
                )
                self.guest_ip = ip_address.stdout.strip()
                break
            except Exception as e:
                print(f"Waiting for VM to start... {e}")
                time.sleep(START_WAIT_TIME)

    def _parse_resolution(result: str):
        match = re.search(r"(\d+)x(\d+)", result)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            return 1920, 1080  # TODO: hacky. handle errors better.

    def read_frame(self):
        """Read a single frame from the VM stream."""
        if not self.ffmpeg_process:
            raise ValueError("Stream receiving not started")

        raw_image = self.ffmpeg_process.stdout.read(
            self.resolution[0] * self.resolution[1] * 3
        )
        if len(raw_image) == 0:
            return None

        # Convert to numpy array
        frame = np.frombuffer(raw_image, dtype=np.uint8).reshape(
            (self.resolution[1], self.resolution[0], 3)
        )
        return frame
