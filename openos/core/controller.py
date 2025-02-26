import socket
import json
from openos.providers import VMWare, VirtualBox, Docker


class Controller:
    """Manages the virtual machine and communication with the VM server."""

    def __init__(
        self,
        os_type: str = "vmware",
        vm_path: str = None,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 120,
        server_port: int = 8765,
        control_port: int = 8766,
    ):
        self.os_type = os_type
        self.vm_path = vm_path
        self.resolution = resolution
        self.fps = fps
        self.server_port = server_port
        self.control_port = control_port
        self.server_ip = None
        self.provider = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        """Start the virtual machine and initialize connection."""
        # Initialize provider
        if self.os_type == "vmware":
            self.provider = VMWare(self.vm_path)
        elif self.os_type == "virtualbox":
            self.provider = VirtualBox(self.vm_path)
        elif self.os_type == "docker":
            self.provider = Docker(self.vm_path)
        else:
            raise NotImplementedError(f"OS type {self.os_type} not supported")

        # Start VM
        self.provider.start()
        self.server_ip = self.provider.get_ip()
        return self.server_ip

    def stop(self):
        """Stop the virtual machine."""
        if self.provider:
            self.provider.stop()

    def reset(self):
        """Reset the virtual machine."""
        if self.provider:
            self.provider.reset()

    def save_state(self, snapshot_name="snapshot"):
        """Save the current state of the VM."""
        if self.provider and hasattr(self.provider, "save_state"):
            self.provider.save_state(snapshot_name)

    def send_input(self, action_type, data):
        """Send input actions to the VM server."""
        if not self.server_ip:
            raise ValueError("VM not started or IP address not available")

        message = json.dumps({"type": action_type, "data": data})
        self.socket.sendto(message.encode(), (self.server_ip, self.control_port))
