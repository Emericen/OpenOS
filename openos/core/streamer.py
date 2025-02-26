import subprocess


class Streamer:
    """Handles video streaming from the VM to clients."""

    def __init__(self, resolution=(1920, 1080), fps=120, port=8765):
        self.resolution = resolution
        self.fps = fps
        self.port = port
        self.client_ip = None
        self.ffmpeg_process = None
        self.streaming = False

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
            f"udp://{self.client_ip}:{self.port}"
        ]
        # fmt: on

        self.ffmpeg_process = subprocess.Popen(cmd)
        self.streaming = True

    def stop_stream(self):
        """Stop the ffmpeg stream."""
        if self.streaming and self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.streaming = False
