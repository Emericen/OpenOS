import time
import json
import socket
import subprocess
import numpy as np

from openos.utils import USER, PASSWORD


class HostService:
    """
    This module runs ON the host machine.

    It handles 3 main functions:
        1. Starting, stopping, resetting, saving, loading the VM.
        2. Sending input commands to the VM (keyboard, mouse, etc.)
        3. Receiving video stream from the VM.
    """

    def __init__(self, vm_path: str, control_port: int = 8765):
        self._vm_path = vm_path
        self._guest_ip = None
        self._control_port = control_port
        self._control_socket = None
        self._frame_buffer = np.memmap(
            filename="/path/to/host/temp/frame.dat",
            # NOTE: ^ this is host's shared folder with guest
            dtype=np.uint8,
            mode="r",
            shape=(1280, 720, 4),
            # NOTE: ^ resolution hardcoded for now. need to send from guest to host (?)
        )

    # -------------- VM Life Cycle Functions --------------

    def start(self):
        subprocess.run(["vmrun", "start", self._vm_path])
        subprocess.run(["vmrun", "enableSharedFolders", self._vm_path, "on"])
        subprocess.run(
            ["vmrun", "enableSharedFolder", self._vm_path, "temp", "/path/to/host/temp"]
        )

        self._guest_ip = self._get_vm_ip(self._vm_path)
        self._control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"VM started. IP address: {self._guest_ip}")

        self._start_guest_service()
        self._send_data({"type": "start_stream", "data": {}})

    def stop(self):
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

    def _start_guest_service(self):
        cmd = ["DISPLAY=:0 /usr/bin/python3 /home/agent/openos/openos/guest.py &"]
        self._execute_commands_in_guest(cmd)

    def _execute_commands_in_guest(self, commands: list[str]):
        # NOTE: cmd output can NOT be seen on host
        combined = " && ".join(commands)
        cmd = f'vmrun -gu {USER} -gp {PASSWORD} runProgramInGuest "{self._vm_path}" /bin/bash -c "{combined}"'
        subprocess.run(cmd, shell=True)

    # -------------- Controller Functions --------------

    # NOTE: feels like there's a lot of room for imagination here.
    #       an AI don't have to restrict its interaction w computer to those of a human.
    #       some immediate ones i can think of: click(x, y), type(long_text), run(cmd) from root, gibberlink mode lol.

    def read_frame(self) -> np.ndarray:
        # TODO: read frame.dat from shared folder with guest
        pass

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
