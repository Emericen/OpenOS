"""
OpenOS FastAPI server.

Exposes REST endpoints for AI agents to control a QEMU virtual machine:
  - Screenshot capture
  - Mouse movement and clicks
  - Keyboard input
  - VM lifecycle (pause, resume, snapshot, etc.)
"""

import io
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from PIL import Image
from pydantic import BaseModel

from qmp import QMPClient

# ── Configuration ────────────────────────────────────────────────

QMP_HOST = os.getenv("QMP_HOST", "localhost")
QMP_PORT = int(os.getenv("QMP_PORT", "4444"))
SCREEN_PATH = "/tmp/screen.ppm"

qmp = QMPClient(host=QMP_HOST, port=QMP_PORT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    qmp.connect()
    yield
    qmp.close()


app = FastAPI(
    title="OpenOS",
    description="AI-agent control plane for a QEMU desktop environment",
    version="0.1.0",
    lifespan=lifespan,
)


# ── Request models ───────────────────────────────────────────────


class MouseMoveRequest(BaseModel):
    x: int
    y: int


class MouseClickRequest(BaseModel):
    button: int = 1  # 1=left, 2=middle, 4=right


class KeyRequest(BaseModel):
    keys: str  # e.g. "ctrl-alt-delete", "a", "ret"
    hold_ms: int | None = None


class TypeRequest(BaseModel):
    text: str
    delay: float = 0.05


class SnapshotRequest(BaseModel):
    name: str


# ── Screenshot ───────────────────────────────────────────────────


@app.get("/screenshot", responses={200: {"content": {"image/png": {}}}})
def screenshot():
    """Capture the current VM screen and return as PNG."""
    try:
        qmp.screendump(SCREEN_PATH)
        img = Image.open(SCREEN_PATH)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(content=buf.read(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Mouse ────────────────────────────────────────────────────────


@app.post("/mouse/move")
def mouse_move(req: MouseMoveRequest):
    """Move the mouse to absolute position (x, y)."""
    try:
        qmp.mouse_move_abs(req.x, req.y)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mouse/click")
def mouse_click(req: MouseClickRequest):
    """Click a mouse button. 1=left, 2=middle, 4=right."""
    try:
        qmp.mouse_click(req.button)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Keyboard ─────────────────────────────────────────────────────


@app.post("/keyboard/key")
def keyboard_key(req: KeyRequest):
    """Send a key combination. E.g. 'ctrl-alt-delete', 'ret', 'a'."""
    try:
        qmp.sendkey(req.keys, req.hold_ms)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/keyboard/type")
def keyboard_type(req: TypeRequest):
    """Type a string character by character."""
    try:
        qmp.type_text(req.text, req.delay)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── VM Lifecycle ─────────────────────────────────────────────────


@app.get("/vm/status")
def vm_status():
    """Get VM running status."""
    try:
        resp = qmp.query_status()
        return resp.get("return", resp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vm/pause")
def vm_pause():
    """Pause the VM."""
    try:
        qmp.vm_pause()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vm/resume")
def vm_resume():
    """Resume a paused VM."""
    try:
        qmp.vm_resume()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vm/reset")
def vm_reset():
    """Hard reset the VM."""
    try:
        qmp.vm_reset()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vm/powerdown")
def vm_powerdown():
    """Send ACPI shutdown to the VM."""
    try:
        qmp.vm_powerdown()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vm/snapshot/save")
def snapshot_save(req: SnapshotRequest):
    """Save a VM snapshot."""
    try:
        qmp.vm_snapshot_save(req.name)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vm/snapshot/load")
def snapshot_load(req: SnapshotRequest):
    """Load a VM snapshot."""
    try:
        qmp.vm_snapshot_load(req.name)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vm/snapshot/delete")
def snapshot_delete(req: SnapshotRequest):
    """Delete a VM snapshot."""
    try:
        qmp.vm_snapshot_delete(req.name)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
