<h1 align="center">📦🖥️ OpenOS</h1>

<p align="center">
  <strong>Spawn a full desktop OS as programmable infrastructure for AI agents.</strong>
</p>

<p align="center">
  A QEMU/KVM-based virtual desktop that runs inside Docker and exposes screenshot, mouse, keyboard, and VM lifecycle controls over a REST API — purpose-built for AI agents that need to interact with a real GUI environment.
</p>

---

## What is this?

AI agents that operate computers need a real desktop to work with — not a browser extension, not an API wrapper, but an actual OS with a display, a mouse, and a keyboard.

**OpenOS** gives you exactly that: a full Ubuntu desktop that boots inside a Docker container and is controllable entirely through HTTP endpoints. An AI agent can take screenshots to see the screen, move the mouse, click buttons, and type on the keyboard — all through a simple REST API.

Under the hood, all control goes through the **QEMU Machine Protocol (QMP)** — the same interface QEMU exposes for programmatic VM management. This means:

- **No guest agent required** — nothing needs to be installed inside the VM
- **Works with any OS** — Ubuntu, Fedora, Windows, anything QEMU can boot
- **Hardware-level input** — mouse and keyboard events are injected at the HID level, indistinguishable from real input

## Quick Start

```bash
# requires a Linux host with KVM enabled
docker compose up -d

# wait for the VM to boot (~30-60s), then:
curl http://localhost:8100/screenshot --output screen.png
curl -X POST http://localhost:8100/mouse/move \
  -H 'Content-Type: application/json' -d '{"x": 500, "y": 300}'
curl -X POST http://localhost:8100/mouse/click \
  -H 'Content-Type: application/json' -d '{"button": 1}'
curl -X POST http://localhost:8100/keyboard/type \
  -H 'Content-Type: application/json' -d '{"text": "hello world"}'
```

## Python SDK

```bash
pip install ./sdk
```

```python
from openos import Desktop

desktop = Desktop("http://localhost:8100")

# see the screen
img = desktop.screenshot()
img.save("screen.png")

# interact
desktop.click(500, 300)
desktop.type_text("hello world")
desktop.key("ret")

# save and restore state
desktop.snapshot_save("clean-state")
# ... do stuff ...
desktop.snapshot_load("clean-state")  # instant rollback
```

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Docker Container                                │
│                                                  │
│  ┌──────────────────┐    ┌────────────────────┐  │
│  │  FastAPI Server   │◄──│  QEMU/KVM          │  │
│  │  :8100            │   │  (Ubuntu Desktop)  │  │
│  │                   │   │                    │  │
│  │  /screenshot      │   │  QMP socket :4444  │  │
│  │  /mouse/*         │   │  VNC display :5900 │  │
│  │  /keyboard/*      │   └────────────────────┘  │
│  │  /vm/*            │                           │
│  └──────────────────┘                            │
│                                                  │
│  ┌──────────────────┐                            │
│  │  NoVNC Web UI     │  (for manual debugging)   │
│  │  :8006            │                           │
│  └──────────────────┘                            │
└──────────────────────────────────────────────────┘
         ▲
         │  HTTP
    AI Agent / SDK
```

## API Reference

### Screen

| Endpoint | Method | Body | Description |
|---|---|---|---|
| `/screenshot` | GET | — | Returns the current screen as a PNG image |

### Mouse

| Endpoint | Method | Body | Description |
|---|---|---|---|
| `/mouse/move` | POST | `{"x": int, "y": int}` | Move mouse to absolute position |
| `/mouse/click` | POST | `{"button": 1\|2\|4}` | Click mouse button (1=left, 2=middle, 4=right) |

### Keyboard

| Endpoint | Method | Body | Description |
|---|---|---|---|
| `/keyboard/key` | POST | `{"keys": str}` | Send key combo, e.g. `ctrl-alt-delete`, `ret`, `a` |
| `/keyboard/type` | POST | `{"text": str}` | Type a string character by character |

### VM Lifecycle

| Endpoint | Method | Body | Description |
|---|---|---|---|
| `/vm/status` | GET | — | Get VM running status |
| `/vm/pause` | POST | — | Pause the VM |
| `/vm/resume` | POST | — | Resume a paused VM |
| `/vm/reset` | POST | — | Hard reset the VM |
| `/vm/powerdown` | POST | — | Send ACPI shutdown signal |
| `/vm/snapshot/save` | POST | `{"name": str}` | Save a named snapshot |
| `/vm/snapshot/load` | POST | `{"name": str}` | Restore a named snapshot |
| `/vm/snapshot/delete` | POST | `{"name": str}` | Delete a named snapshot |

## How It Works: QMP

All VM control goes through the [QEMU Machine Protocol (QMP)](https://www.qemu.org/docs/master/interop/qmp-spec.html) — a JSON-based protocol for programmatic QEMU management.

The FastAPI server connects to QEMU's QMP socket and translates REST calls into QMP commands:

```
Screenshot  →  {"execute": "screendump", "arguments": {"filename": "/tmp/screen.ppm"}}
Mouse move  →  {"execute": "human-monitor-command", "arguments": {"command-line": "mouse_move 500 300"}}
Mouse click →  {"execute": "human-monitor-command", "arguments": {"command-line": "mouse_button 1"}}
Key press   →  {"execute": "human-monitor-command", "arguments": {"command-line": "sendkey ctrl-alt-delete"}}
VM pause    →  {"execute": "stop"}
VM resume   →  {"execute": "cont"}
VM snapshot →  {"execute": "human-monitor-command", "arguments": {"command-line": "savevm clean-state"}}
```

The `human-monitor-command` wrapper lets us use QEMU's Human Monitor Protocol (HMP) commands — like `mouse_move`, `mouse_button`, and `sendkey` — over the structured QMP interface. These commands inject input at the hardware level, so the guest OS sees them as real HID events.

For the full QMP spec, see: [QEMU QMP Specification](https://www.qemu.org/docs/master/interop/qmp-spec.html)

## Configuration

Environment variables (set in `compose.yml`):

| Variable | Default | Description |
|---|---|---|
| `BOOT` | `ubuntu` | OS to boot ([full list](upstream/readme.md)) |
| `RAM_SIZE` | `4G` | VM memory allocation |
| `CPU_CORES` | `2` | Number of virtual CPU cores |
| `DISK_SIZE` | `64G` | Virtual disk size |
| `API_PORT` | `8100` | Port for the OpenOS REST API |

You can also set `BOOT` to a URL to boot any custom `.iso`, `.img`, or `.qcow2` image.

## Web UI

A NoVNC web viewer is available at `http://localhost:8006` for visual debugging and manual interaction with the VM.

## Requirements

- **Linux host with KVM** (`/dev/kvm` must be available)
- **Docker** with compose support
- See the [upstream FAQ](upstream/readme.md#how-do-i-verify-if-my-system-supports-kvm) for KVM troubleshooting

## Project Structure

```
OpenOS/
├── api/
│   ├── qmp.py          # QMP client — connects to QEMU's control socket
│   └── server.py       # FastAPI server — REST API for AI agents
├── scripts/
│   └── entry.sh        # Container entrypoint — boots QEMU + starts API
├── sdk/
│   ├── openos.py       # Python SDK for agent developers
│   └── pyproject.toml
├── upstream/            # vendored from qemus/qemu (git subtree)
├── Dockerfile
├── compose.yml
└── README.md
```

## Acknowledgments

The QEMU/Docker infrastructure is built on top of [**qemus/qemu**](https://github.com/qemus/qemu) by [**kroese**](https://github.com/kroese) — a well-engineered Docker container for running virtual machines with QEMU. Their work handles the heavy lifting of VM boot, disk management, networking, and display, which OpenOS extends with the AI-agent control plane.

## License

The upstream QEMU container is licensed under its [original terms](upstream/license.md). The OpenOS additions (API server, SDK, entry script) are MIT licensed.
