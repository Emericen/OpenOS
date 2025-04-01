import json
import socket
import subprocess
import numpy as np
from pathlib import Path
from openos.utils import USER, PASSWORD, SHARED_FOLDER_NAME, configure_logger

logger = configure_logger(__name__)


class HostService:
    """
    This module runs on the host machine.

    It handles 3 main functions:
        1. Managing the VM's life cycle.
        2. Sending input commands to the VM (keyboard, mouse, etc.)
        3. Reading the VM's frame buffer.
    """

    def __init__(self, cache_dir: Path, vm_path: str, headless: bool = False):
        self._headless = headless
        self._vm_path = vm_path
        self._cache_dir = cache_dir
        self._shared_folder_path = cache_dir / SHARED_FOLDER_NAME

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
        self._control_port = 8765  # TODO: should we not hardcode this?

    # -------------- VM Life Cycle Functions --------------

    def start(self):
        logger.info(f"Starting VM at {self._vm_path}")
        gui_flag = "gui" if not self._headless else "nogui"
        subprocess.run(["vmrun", "start", self._vm_path, gui_flag], check=True)

        logger.info("Waiting for VM to be ready...")
        self._guest_ip = self._get_vm_ip()

        logger.info(f"Enabling shared folders for {self._vm_path}")
        subprocess.run(["vmrun", "enableSharedFolders", self._vm_path, "on"])

        logger.info(
            f"Enabling shared folder {self._shared_folder_path} for {self._vm_path}"
        )
        subprocess.run(
            [
                "vmrun",
                "addSharedFolder",
                self._vm_path,
                SHARED_FOLDER_NAME,
                self._shared_folder_path,
            ]
        )

        logger.info(f"Starting guest service at {self._shared_folder_path}")
        self._install_guest_client()
        cmd = ["DISPLAY=:0 /usr/bin/python3.10 /home/user/openos/openos/guest.py &"]
        self._execute_commands_in_guest(cmd)

    def stop(self):
        logger.info(
            f"Removing shared folder {self._shared_folder_path} from {self._vm_path}"
        )
        subprocess.run(
            ["vmrun", "removeSharedFolder", self._vm_path, SHARED_FOLDER_NAME]
        )
        logger.info(f"Stopping VM at {self._vm_path}")
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

    def _install_guest_client(self):
        commands = [
            'cd ~ && if [ -d "openos" ]; then cd openos && git pull && cd .. ; else git clone https://github.com/Emericen/openos.git; fi',
            "cd openos && pip install . --force-reinstall",
        ]
        self._execute_commands_in_guest(commands)

    def _get_vm_ip(self):
        command = f'vmrun getGuestIPAddress "{self._vm_path}" -wait'
        result = subprocess.run(
            command, shell=True, text=True, capture_output=True, encoding="utf-8"
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.error(f"Failed to get the IP of virtual machine: {result.stderr}")
            return None

    # -------------- Controller Functions --------------

    # NOTE: feels like there's a lot of room for imagination here.
    #       an AI doesn't have to restrict to ways a human interacts with computer.
    #       some other cmds i can think of: click(x, y), type(long_text), run(cmd) from root, gibberlink mode lol.

    def read_frame(self) -> np.ndarray:
        return self._frame_buffer

    def position_mouse(self, x, y):
        self._send_data({"type": "position_mouse", "data": {"x": x, "y": y}})

    def move_mouse(self, dx, dy):
        self._send_data({"type": "move_mouse", "data": {"dx": dx, "dy": dy}})

    def mouse_button_down(self, button):
        self._send_data({"type": "button_down", "data": {"button": button}})

    def mouse_button_up(self, button):
        self._send_data({"type": "button_up", "data": {"button": button}})

    def scroll(self, dx, dy):
        self._send_data({"type": "scroll", "data": {"dx": dx, "dy": dy}})

    def keyboard_key_down(self, key):
        self._send_data({"type": "key_down", "data": {"key": key}})

    def keyboard_key_up(self, key):
        self._send_data({"type": "key_up", "data": {"key": key}})

    def _send_data(self, data: dict):
        if not self._guest_ip:
            raise ValueError("VM not started or IP address not available")
        data = json.dumps(data)
        self._control_socket.sendto(data.encode(), (self._guest_ip, self._control_port))
