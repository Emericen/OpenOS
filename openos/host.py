import time
import json
import subprocess
import numpy as np
from pathlib import Path

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
            empty_frame_buffer = np.zeros((1280, 720, 4), dtype=np.uint8)
            empty_frame_buffer.tofile(self._shared_folder_path / "frame_buffer.dat")
            empty_control_buffer = []
            with open(self._shared_folder_path / "control_buffer.json", "w") as f:
                json.dump(empty_control_buffer, f)

        self._frame_buffer = np.memmap(
            filename=f"{self._shared_folder_path}/frame_buffer.dat",
            dtype=np.uint8,
            mode="r",
            shape=(1280, 720, 4),  # TODO: get from guest
        )
        self._control_buffer = []
        self._control_buffer_path = f"{self._shared_folder_path}/control_buffer.json"

    # -------------- VM Life Cycle Functions --------------

    def start(self):
        # fmt: off
        print(f"Starting VM at {self._vm_path}")
        subprocess.run(["vmrun", "start", self._vm_path])
        self._wait_for_vm_ready()
        print(f"Enabling shared folders for {self._vm_path}")
        subprocess.run(["vmrun", "enableSharedFolders", self._vm_path, "on"])
        print(f"Enabling shared folder {self._shared_folder_path} for {self._vm_path}")
        subprocess.run(["vmrun", "addSharedFolder", self._vm_path, "temp", self._shared_folder_path])
        print(f"Starting guest service at {self._shared_folder_path}")
        # "DISPLAY=:0 /usr/bin/python3 /home/agent/openos/openos/guest.py &",
        cmd = ["cd /home/user/openos", "python openos/guest.py &"]
        self._execute_commands_in_guest(cmd)
        # fmt: on

    def stop(self):
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

    def _wait_for_vm_ready(self):
        vm_ready = False
        while not vm_ready:
            try:
                result = subprocess.run(
                    ["vmrun", "checkToolsState", self._vm_path],
                    capture_output=True,
                    text=True,
                )
                if "running" in result.stdout.lower():
                    vm_ready = True
                    print("VM is ready!")
                else:
                    print("VM still starting, waiting...")
                    time.sleep(5)
            except Exception as e:
                print(f"Error checking VM state: {e}")
                time.sleep(5)

    # -------------- Controller Functions --------------

    # NOTE: feels like there's a lot of room for imagination here.
    #       an AI don't have to restrict its interaction w computer to those of a human.
    #       some immediate ones i can think of: click(x, y), type(long_text), run(cmd) from root, gibberlink mode lol.

    def read_frame(self) -> np.ndarray:
        # TODO: read frame.dat from shared folder with guest
        pass

    def position_mouse(self, x, y):
        self._write_to_buffer({"type": "position_mouse", "data": {"x": x, "y": y}})

    def move_mouse(self, dx, dy):
        self._write_to_buffer({"type": "move_mouse", "data": {"dx": dx, "dy": dy}})

    def button_down(self, button):
        self._write_to_buffer({"type": "button_down", "data": {"button": button}})

    def button_up(self, button):
        self._write_to_buffer({"type": "button_up", "data": {"button": button}})

    def scroll(self, dx, dy):
        self._write_to_buffer({"type": "scroll", "data": {"dx": dx, "dy": dy}})

    def key_down(self, key):
        self._write_to_buffer({"type": "key_down", "data": {"key": key}})

    def key_up(self, key):
        self._write_to_buffer({"type": "key_up", "data": {"key": key}})

    def _write_to_buffer(self, data: dict):
        data["role"] = "host"
        self._control_buffer.append(data)
        if len(self._control_buffer) > 100:
            self._control_buffer = self._control_buffer[-100:]

        with open(self._control_buffer_path, "w") as f:
            json.dump(self._control_buffer, f)

    def _read_from_buffer(self):
        with open(self._control_buffer_path, "r") as f:
            self._control_buffer = json.load(f)
        message = self._control_buffer[-1]
        # TODO: get status including resolution, etc.
