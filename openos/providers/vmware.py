import os
import platform
import subprocess
from openos.providers.base import OperatingSystem


UBUNTU_ARM_URL = "https://example.com/ubuntu-arm.zip"
UBUNTU_X86_URL = "https://example.com/ubuntu-x86.zip"
WINDOWS_X86_URL = "https://example.com/windows-x86.zip"


class VMWare(OperatingSystem):
    def __init__(self, vm_path=None):
        self.vm_path = vm_path

    def start(self):
        subprocess.run(["vmrun", "start", self.vm_path])

    def stop(self):
        subprocess.run(["vmrun", "stop", self.vm_path])

    def reset(self):
        subprocess.run(["vmrun", "reset", self.vm_path])

    def get_ip(self):
        result = subprocess.run(
            ["vmrun", "getGuestIPAddress", self.vm_path], capture_output=True, text=True
        )
        return result.stdout.strip()
