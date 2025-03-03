import time
import json
import socket
import subprocess
import numpy as np

from openos.utils import get_ubuntu_vm_path
from openos.utils import USER, PASSWORD, GUEST_TEMP_OUTPUT_FILE

START_WAIT_TIME = 10  # seconds


class HostService:
    """Manages the virtual machine and communication with the VM server."""

    def __init__(
        self, video_port: int = 8765, control_port: int = 8766, cache_dir: str = None
    ):
        self.guest_ip = None
        self.video_port = video_port
        self.control_port = control_port

        self.ffmpeg_process = None
        self.control_socket = None

        # self.vm_path = get_ubuntu_vm_path(cache_dir=cache_dir)
        self.cache_dir = (
            "/Users/eddyliang/Desktop/workfile/OSWorld/vmware_vm_data/Ubuntu0/"
        )
        self.vm_path = "/Users/eddyliang/Desktop/workfile/OSWorld/vmware_vm_data/Ubuntu0/Ubuntu0.vmx"
        self.resolution = None

    def start(self):
        # Start the guest
        print(f"Starting VM: {self.vm_path}")
        subprocess.run(["vmrun", "start", self.vm_path])
        print("waiting ip address...")
        self.guest_ip = self._get_vm_ip(self.vm_path)
        print(f"VM started. IP address: {self.guest_ip}")

        # Start the guest service
        print("running guest.py...")
        cmd = ["cd ~/OpenOS", "python openos/guest.py"]
        self._execute_commands_in_guest(cmd)

        self.resolution = (1920, 1080)  # TODO: make dynamic (?)

        # Set up the control socket
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # fmt: off
        print("starting ffmpeg...")
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
        if not self.guest_ip:
            raise ValueError("VM not started or IP address not available")
        data = json.dumps(data)
        self.control_socket.sendto(data.encode(), (self.guest_ip, self.control_port))

    def _execute_commands_in_guest(self, commands: list[str]):
        # NOTE: no output can be seen on host
        combined = " && ".join(commands)
        cmd = f'vmrun -gu {USER} -gp {PASSWORD} runProgramInGuest "{self.vm_path}" /bin/bash -c "{combined}"'
        subprocess.run(cmd, shell=True)

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


if __name__ == "__main__":
    try:
        host = HostService()
        host.start()
        total_time = 120

        direction = 0
        for remaining in range(total_time, 0, -1):
            print(f"\rTime remaining: {remaining:3d} seconds", end="")

            if direction == 0:
                host.move_mouse(100, 0)
            elif direction == 1:
                host.move_mouse(0, 100)
            elif direction == 2:
                host.move_mouse(-100, 0)
            elif direction == 3:
                host.move_mouse(0, -100)
            direction = (direction + 1) % 4

            time.sleep(1)
        print("\nShutting down...")
        host.stop()
    except KeyboardInterrupt:
        host.stop()
        print("GuestService stopped")
