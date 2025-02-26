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
# User API example
from openos import OpenOS

# For human interaction with GUI
ubuntu = OpenOS.create("ubuntu", interface="gui")
ubuntu.start()

# For AI agent (headless)
windows = OpenOS.create("windows", interface="headless") 
windows.start()
frames = windows.get_frames(count=10)  # Get recent frames for AI
windows.execute_action(action)  # Send commands
```