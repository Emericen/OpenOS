import time
import json
import socket
import platform
import subprocess
from pathlib import Path
from huggingface_hub import hf_hub_download

START_WAIT_TIME = 10  # seconds
REPO_ID = "xlangai/ubuntu_osworld"
UBUNTU_ARM_FILENAME = "Ubuntu-arm.zip"
UBUNTU_X86_FILENAME = "Ubuntu-x86.zip"
# Create cache directory
CACHE_DIR = Path.home() / ".cache" / "openos"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class HostService:
    """Manages the virtual machine and communication with the VM server."""

    def __init__(self, video_port: int = 8765, control_port: int = 8766):
        self.guest_ip = None
        self.video_port = video_port
        self.control_port = control_port

        self.ffmpeg_process = None
        self.control_socket = None

        self.vm_path = self._install_ubuntu()
        self.resolution = None

    def start(self):
        subprocess.run(["vmrun", "start", self.vm_path])
        self._wait_for_ip_address()

        # Set up the control socket
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Send setup message to guest and wait for resolution response
        self._send_data({"type": "setup", "data": {}})
        
        # Wait for resolution info from guest
        self._receive_resolution()
        
        # Now we can start ffmpeg with the correct resolution
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

    def _install_ubuntu(self):
        # First check if VM is already unpacked
        vmx_files = list(CACHE_DIR.glob("*.vmx"))
        if vmx_files:
            self.vm_path = str(vmx_files[0])
            print(f"Using existing VM image at {self.vm_path}")
            return self.vm_path

        # Check platform architecture
        machine = platform.machine().lower()
        if machine in ["arm64", "aarch64"]:
            filename = UBUNTU_ARM_FILENAME
        elif machine in ["amd64", "x86_64"]:
            filename = UBUNTU_X86_FILENAME
        else:
            raise Exception("Unsupported platform or architecture.")

        # Download using huggingface_hub
        print(f"Downloading Ubuntu VM image from {REPO_ID}")
        zip_path = hf_hub_download(
            repo_id=REPO_ID, filename=filename, cache_dir=CACHE_DIR
        )

        # Extract with subprocess
        print(f"Extracting VM image to {CACHE_DIR}")
        subprocess.run(["unzip", "-o", str(zip_path), "-d", str(CACHE_DIR)])

        # Find the VMX file
        vmx_files = list(CACHE_DIR.glob("*.vmx"))
        self.vm_path = str(vmx_files[0])
        print(f"VM image installed at {self.vm_path}")
        return self.vm_path

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

    def _receive_resolution(self):
        """Wait for resolution information from the guest."""
        # Set a timeout for receiving data
        self.control_socket.settimeout(5)
        try:
            data, addr = self.control_socket.recvfrom(1024)
            message = json.loads(data.decode())
            if message["type"] == "resolution":
                width = message["data"]["width"]
                height = message["data"]["height"]
                self.resolution = (width, height)
                print(f"Received resolution from guest: {width}x{height}")
        except socket.timeout:
            print("Timeout waiting for resolution, using default")
            self.resolution = (1920, 1080)  # Default fallback
        finally:
            # Reset to non-blocking mode
            self.control_socket.settimeout(None)

    # def read_frame(self):
    #     """Read a single frame from the VM stream."""
    #     if not self.ffmpeg_process:
    #         raise ValueError("Stream receiving not started")

    #     raw_image = self.ffmpeg_process.stdout.read(
    #         self.resolution[0] * self.resolution[1] * 3
    #     )
    #     if len(raw_image) == 0:
    #         return None

    #     # Convert to numpy array
    #     frame = np.frombuffer(raw_image, dtype=np.uint8).reshape(
    #         (self.resolution[1], self.resolution[0], 3)
    #     )
    #     return frame
