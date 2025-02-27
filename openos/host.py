import socket
import json
import subprocess
import time
import platform
import requests
import numpy as np
from tqdm import tqdm
from pathlib import Path

START_WAIT_TIME = 10  # seconds
UBUNTU_ARM_URL = (
    "https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu-arm.zip"
)
UBUNTU_X86_URL = (
    "https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu-x86.zip"
)
# Create cache directory
CACHE_DIR = Path.home() / ".cache" / "openos"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class HostService:
    """Manages the virtual machine and communication with the VM server."""

    def __init__(
        self,
        # vm_path: str = None,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 120,
        output_port: int = 8765,
        input_port: int = 8766,
    ):
        self.vm_path = self._install_ubuntu()
        self.resolution = resolution
        self.fps = fps
        self.output_port = output_port
        self.input_port = input_port
        self.server_ip = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ffmpeg_process = None

    def start(self):
        subprocess.run(["vmrun", "start", self.vm_path])

        # Wait for VM to start
        while True:
            try:
                self.server_ip = self.provider.get_ip()
                break
            except Exception as e:
                print(f"Waiting for VM to start... {e}")
                time.sleep(START_WAIT_TIME)

        self.server_ip = self.provider.get_ip()
        return self.server_ip

    def stop(self):
        subprocess.run(["vmrun", "stop", self.vm_path])

    def reset(self):
        subprocess.run(["vmrun", "reset", self.vm_path])

    def save(self, snapshot_name="snapshot"):
        """Save the current state of the VM."""
        subprocess.run(["vmrun", "saveSnapshot", self.vm_path, snapshot_name])

    def load(self, snapshot_name="snapshot"):
        """Load a saved state of the VM."""
        subprocess.run(["vmrun", "loadSnapshot", self.vm_path, snapshot_name])

    def send_input(self, action_type, data):
        """Send input actions to the VM server."""
        if not self.server_ip:
            raise ValueError("VM not started or IP address not available")

        message = json.dumps({"type": action_type, "data": data})
        self.socket.sendto(message.encode(), (self.server_ip, self.input_port))

    def get_ip(self):
        result = subprocess.run(
            ["vmrun", "getGuestIPAddress", self.vm_path], capture_output=True, text=True
        )
        return result.stdout.strip()

    def _install_ubuntu(self):
        # Check platform architecture
        machine = platform.machine().lower()
        if machine in ["arm64", "aarch64"]:
            url = UBUNTU_ARM_URL
        elif machine in ["amd64", "x86_64"]:
            url = UBUNTU_X86_URL
        else:
            raise Exception("Unsupported platform or architecture.")

        # Create cache directory
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        zip_path = CACHE_DIR / "ubuntu.zip"

        # Download with progress bar
        print(f"Downloading Ubuntu VM image from {url}")
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))

        with (
            open(zip_path, "wb") as f,
            tqdm(
                desc="Downloading",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar,
        ):
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)

        # Extract with subprocess
        print(f"Extracting VM image to {CACHE_DIR}")
        subprocess.run(["unzip", "-o", str(zip_path), "-d", str(CACHE_DIR)])

        # Remove zip file
        print("Cleaning up downloaded zip file")
        zip_path.unlink()

        # Return path to VM file
        vmx_files = list(CACHE_DIR.glob("*.vmx"))
        if not vmx_files:
            print("No .vmx file found in the extracted directory")
            raise Exception("No .vmx file found in the extracted directory")

        self.vm_path = str(vmx_files[0])
        print(f"VM image installed at {self.vm_path}")
        return self.vm_path

    def start_receiving(self):
        """Start receiving the ffmpeg stream from VM."""
        if not self.server_ip:
            raise ValueError("VM not started or IP address not available")

        # fmt: off
        cmd = [
            "ffmpeg", "-fflags", "nobuffer", 
            "-f", "mpegts", 
            "-i", f"udp://{self.server_ip}:{self.output_port}", 
            "-f", "rawvideo", 
            "-flags", "low_delay", 
            "-avioflags", "direct", 
            "-pix_fmt", "rgb24", 
            "-vf", "format=rgb24", 
            "pipe:1"
        ]
        # fmt: on

        self.ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return self.ffmpeg_process

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

    def stop_receiving(self):
        """Stop receiving the ffmpeg stream."""
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None
