# OpenOS

OpenOS is a Python interactable operating system for both human and AI agents.

# Quick Start

Make sure you have VMware installed. Test by running

```bash
vmrun list
```

You should see a list of VMs. Now you're ready to install OpenOS, simply run

```bash
pip install openos
```

Use OpenOS like this:

```python
from openos import OpenOS

ubuntu = OpenOS.create()
ubuntu.start()

# Interact with the OS
ubuntu.move_mouse(100, 120)
ubuntu.button_down("mouse.Button.left")
ubuntu.button_up("mouse.Button.left")

# Capture and display the current screen as an BGRA array of size (720, 1280, 4)
# NOTE: While read can be called anytime, frame data itself updates at ~30 FPS.
frame = ubuntu.read_frame()

# Shuts down the VM
ubuntu.stop()
```

## To Setup New Ubuntu VM

1. Install iso from [official site](https://releases.ubuntu.com/jammy/). on windows, select [ubuntu-22.04.5-desktop-amd64.iso](https://releases.ubuntu.com/jammy/ubuntu-22.04.5-desktop-amd64.iso).
2. Open VMWare and create new VM with the ISO. Select automatic login without password.
3. After OS is ready, copy and paste code in `openos\scripts\ubuntu-setup.sh` and run it. Here's what I did:
    ```bash
    user@ubuntu:~$ cd Desktop
    user@ubuntu:~$ touch setup.sh
    user@ubuntu:~$ open setup.sh # paste in the code
    user@ubuntu:~$ chmod +x setup.sh
    user@ubuntu:~$ sudo ./setup.sh
    ```

4. Logout of the OS and log back in. When entering password, select the gear icon on bottom right and switch to `Ubuntu on Xorg`.
5. Log back in, right click anywhere, and go to `Display Settings`. Change resolution to `1280x720`.

## Future Work

- Switch from VMWare to Qemu / KVM
  - Open source and faster and native to linux.
  - Has GPU pass-through.
  - Allows for more control to add more docker-like features s.a. building, hot reloading, and logging.
  - See [1](https://www.youtube.com/watch?v=Kq849CpGd88) and [2](https://www.youtube.com/watch?v=BgZHbCDFODk)
- Add Windows as selectable OS.
- Add Audio support (?)
  - Consider using `pyaudio` or `ffmpeg`
- Add more types of controls (?) 
  - See comments in [host.py](openos/host.py)
