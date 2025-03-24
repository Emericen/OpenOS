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
import time
from openos import OpenOS

ubuntu = OpenOS.create()
ubuntu.start()
ubuntu.move_mouse(100, 120)
ubuntu.button_down("mouse.Button.left")
ubuntu.button_up("mouse.Button.left")
ubuntu.stop()
```

## To setup New Ubuntu VM

1. Install iso from [official site](https://releases.ubuntu.com/jammy/). on windows, select [ubuntu-22.04.5-desktop-amd64.iso](https://releases.ubuntu.com/jammy/ubuntu-22.04.5-desktop-amd64.iso).

2. Open VMWare and create new VM with the ISO.

3. After OS is ready, copy and paste code in `openos\scripts\ubuntu-setup.sh` and run it. Here's what I did:
    ```bash
    user@ubuntu:~$ cd Desktop
    user@ubuntu:~$ touch setup.sh
    user@ubuntu:~$ open setup.sh # paste in the code
    user@ubuntu:~$ chmod +x setup.sh
    user@ubuntu:~$ sudo ./setup.sh
    ```

4. Go to power button on top right and logout. When logging back in and entering password, select the gear icon on bottom right and switch to `Ubuntu on Xorg`.
5. Log back in, right click anywhere, and go to `Display Settings`. Change resolution to `1280x720`.