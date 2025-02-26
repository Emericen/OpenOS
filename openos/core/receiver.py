import subprocess
import numpy as np


class Receiver:
    """Handles receiving video streams from the VM server."""

    def __init__(self, server_ip, server_port, resolution):
        self.server_ip = server_ip
        self.server_port = server_port
        self.resolution = resolution
        self.ffmpeg_process = None

    def start_receiving(self):
        """Start receiving the ffmpeg stream from server."""

        # fmt: off
        cmd = [
            "ffmpeg", "-fflags", "nobuffer", 
            "-f", "mpegts", 
            "-i", f"udp://{self.server_ip}:{self.server_port}", 
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
        """Read a single frame from the stream."""
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
