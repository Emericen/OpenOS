import json
import socket
import subprocess
import numpy as np
from pathlib import Path
import shutil

# from openos.utils import USER, PASSWORD

USER = "user"
PASSWORD = "password"


class HostService:
    """
    This module runs ON the host machine.

    It handles 3 main functions:
        1. Starting, stopping, resetting, saving, loading the VM.
        2. Sending input commands to the VM (keyboard, mouse, etc.)
        3. Receiving video stream from the VM.
    """

    def __init__(self, cache_dir: Path, vm_path: str):
        self._vm_path = vm_path
        self._cache_dir = cache_dir
        self._shared_folder_path = cache_dir / "temp"

        if not self._shared_folder_path.exists():
            self._shared_folder_path.mkdir(parents=True, exist_ok=True)
            empty_frame_buffer = np.zeros((720, 1280, 4), dtype=np.uint8)
            empty_frame_buffer.tofile(self._shared_folder_path / "frame_buffer.dat")

        self._frame_buffer = np.memmap(
            filename=f"{self._shared_folder_path}/frame_buffer.dat",
            dtype=np.uint8,
            mode="r",
            shape=(720, 1280, 4),  # TODO: get from guest
        )

        # Control socket for sending commands to guest
        self._control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._control_port = 8765 # TODO: should we not hardcode this?

    # -------------- VM Life Cycle Functions --------------

    def start(self):
        # fmt: off
        print(f"Starting VM at {self._vm_path}")
        subprocess.run(["vmrun", "start", self._vm_path])
        print("Waiting for VM to be ready...")
        self._guest_ip = self._get_vm_ip() # wait for vm ready
        print(f"Enabling shared folders for {self._vm_path}")
        subprocess.run(["vmrun", "enableSharedFolders", self._vm_path, "on"])
        print(f"Enabling shared folder {self._shared_folder_path} for {self._vm_path}")
        subprocess.run(["vmrun", "addSharedFolder", self._vm_path, "temp", self._shared_folder_path])
        print(f"Starting guest service at {self._shared_folder_path}")
        # "DISPLAY=:0 /usr/bin/python3 /home/agent/openos/openos/guest.py &",
        # cmd = ["cd /home/user/openos", "python openos/guest.py &"]
        cmd = ["DISPLAY=:0 /usr/bin/python3.10 /home/user/openos/openos/guest.py &"]
        self._execute_commands_in_guest(cmd)
        # fmt: on

    def stop(self):
        print(f"Removing shared folder {self._shared_folder_path} from {self._vm_path}")
        subprocess.run(["vmrun", "removeSharedFolder", self._vm_path, "temp"])
        shutil.rmtree(self._shared_folder_path)
        print(f"Stopping VM at {self._vm_path}")
        subprocess.run(["vmrun", "stop", self._vm_path])

    def reset(self):
        subprocess.run(["vmrun", "reset", self._vm_path])

    def save(self, snapshot_name="snapshot"):
        subprocess.run(["vmrun", "saveSnapshot", self._vm_path, snapshot_name])

    def load(self, snapshot_name="snapshot"):
        subprocess.run(["vmrun", "loadSnapshot", self._vm_path, snapshot_name])

    def _execute_commands_in_guest(self, commands: list[str]):
        # NOTE: cmd output can NOT be seen on host
        combined = " && ".join(commands)
        cmd = f'vmrun -gu {USER} -gp {PASSWORD} runProgramInGuest "{self._vm_path}" /bin/bash -c "{combined}"'
        subprocess.run(cmd, shell=True)

    def _get_vm_ip(self):
        command = f'vmrun getGuestIPAddress "{self._vm_path}" -wait'
        result = subprocess.run(
            command, shell=True, text=True, capture_output=True, encoding="utf-8"
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Failed to get the IP of virtual machine: {result.stderr}")
            return None

    # -------------- Controller Functions --------------

    # NOTE: feels like there's a lot of room for imagination here.
    #       an AI don't have to restrict its interaction w computer to those of a human.
    #       some immediate ones i can think of: click(x, y), type(long_text), run(cmd) from root, gibberlink mode lol.

    def read_frame(self) -> np.ndarray:
        # TODO: read frame_buffer.dat and return numpy array for Agent
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
