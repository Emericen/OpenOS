import time
import json
import socket
import subprocess
import numpy as np

from openos.utils import USER, PASSWORD


class HostService:
    """Manages the virtual machine and communication with the VM server."""

    def __init__(self, vm_path: str, video_port: int = 8765, control_port: int = 8766):
        self._vm_path = vm_path
        self._guest_ip = None
        self._video_port = video_port
        self._control_port = control_port
        self._resolution = (1280, 720)  # NOTE: hardcoded for now

        self._ffmpeg_process = None
        self._control_socket = None

    # -------------- VM Life Cycle Functions --------------

    def start(self):
        subprocess.run(["vmrun", "start", self._vm_path])
        self._guest_ip = self._get_vm_ip(self._vm_path)
        print(f"VM started. IP address: {self._guest_ip}")

        self._start_guest_service()
        self._control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # fmt: off
        print("starting ffmpeg...")
        cmd = [
            "ffmpeg", "-fflags", "nobuffer", 
            "-f", "mpegts", 
            "-i", f"udp://{self._guest_ip}:{self._video_port}", 
            "-f", "mpegts", 
            "-flags", "low_delay", 
            "-avioflags", "direct", 
            "-pix_fmt", "rgb24", 
            "-vf", "format=rgb24", 
            "pipe:1"
        ]
        # fmt: on
        self._ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    def stop(self):
        if self._ffmpeg_process:
            self._ffmpeg_process.terminate()
            self._ffmpeg_process.wait()
            self._ffmpeg_process = None
        if self._control_socket:
            self._control_socket.close()
            self._control_socket = None
        subprocess.run(["vmrun", "stop", self._vm_path])

    def reset(self):
        subprocess.run(["vmrun", "reset", self._vm_path])

    def save(self, snapshot_name="snapshot"):
        subprocess.run(["vmrun", "saveSnapshot", self._vm_path, snapshot_name])

    def load(self, snapshot_name="snapshot"):
        subprocess.run(["vmrun", "loadSnapshot", self._vm_path, snapshot_name])

    def _execute_commands_in_guest(self, commands: list[str]):
        # NOTE: no output can be seen on host
        combined = " && ".join(commands)
        cmd = f'vmrun -gu {USER} -gp {PASSWORD} runProgramInGuest "{self._vm_path}" /bin/bash -c "{combined}"'
        subprocess.run(cmd, shell=True)

    def _start_guest_service(self):
        cmd = ["DISPLAY=:0 /usr/bin/python3 /home/agent/openos/openos/guest.py &"]
        self._execute_commands_in_guest(cmd)

    def _get_vm_ip(self, vm_path: str):
        command = f'vmrun getGuestIPAddress "{vm_path}" -wait'
        result = subprocess.run(
            command, shell=True, text=True, capture_output=True, encoding="utf-8"
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Failed to get the IP of virtual machine: {result.stderr}")
            return None

    # -------------- Controller Functions --------------

    def read_frame(self):
        raw_image = self._ffmpeg_process.stdout.read(
            self._resolution[0] * self._resolution[1] * 3
        )
        if len(raw_image) == 0:
            return None

        # Convert to numpy array
        frame = np.frombuffer(raw_image, dtype=np.uint8).reshape(
            (self._resolution[1], self._resolution[0], 3)
        )
        return frame

    def position_mouse(self, x, y):
        self._send_data({"type": "position_mouse", "data": {"x": x, "y": y}})

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
        if not self._guest_ip:
            raise ValueError("VM not started or IP address not available")
        data = json.dumps(data)
        self._control_socket.sendto(data.encode(), (self._guest_ip, self._control_port))
