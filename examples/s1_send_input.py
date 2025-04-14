import sys
import time
import json
import websocket


def move_mouse(ws: websocket.WebSocket, x: int, y: int):
    ws.send(json.dumps({"type": "mouse_position", "data": {"x": x, "y": y}}))


def type_letter(ws: websocket.WebSocket, letter: str, capitalize: bool = False):
    if capitalize:
        ws.send(json.dumps({"type": "keyboard_key_down", "data": {"key": "shift"}}))
        time.sleep(0.01)
    ws.send(json.dumps({"type": "keyboard_key_down", "data": {"key": letter}}))
    time.sleep(0.01)
    ws.send(json.dumps({"type": "keyboard_key_up", "data": {"key": letter}}))
    if capitalize:
        ws.send(json.dumps({"type": "keyboard_key_up", "data": {"key": "shift"}}))
    time.sleep(0.05)


def scroll_down(ws: websocket.WebSocket):
    ws.send(json.dumps({"type": "mouse_scroll", "data": {"btn": "wheel-down"}}))
    time.sleep(0.05)


def scroll_up(ws: websocket.WebSocket):
    ws.send(json.dumps({"type": "mouse_scroll", "data": {"btn": "wheel-up"}}))
    time.sleep(0.05)


def view_frame(ws: websocket.WebSocket):
    ws.send(json.dumps({"type": "screenshot", "data": {}}))


if __name__ == "__main__":

    ws_url = "ws://localhost:8007"
    ws = websocket.WebSocket(enable_multithread=True)
    ws.settimeout(10)
    ws.connect(ws_url, timeout=10)

    """
    USAGE GUIDE
    ===========
    
    Launch guest with `docker compose up -d`. Go into guest by visiting `http://localhost:8006`.

    Open terminal, and run `sudo mount -t 9p -o trans=virtio shared /mnt/example`.

    After that, you can run this script to send input to the guest.
    
    This script provides utilities for controlling mouse movement, keyboard input, 
    and scrolling in a WebSocket environment.
    
    Mouse Positioning:
      python test.py mouse <x> <y>
      
      Parameters:
        x, y: Position coordinates (0-100)
              Values are automatically scaled to the 0-32767 range used by the system
      
      Example:
        python test.py mouse 50 50  # Moves cursor to the center of the screen

      NOTE: QMP screenshot does not have cursor shown, so you might not be able to visualize this. Display streaming with `mss(with_cursor=True)` is recommended and is WIP.
    Scrolling:
      python test.py scroll <direction>
      
      Parameters:
        direction: Either "up" or "down"
      
      Examples:
        python test.py scroll down  # Scrolls down one increment
        python test.py scroll up    # Scrolls up one increment
    
    Keyboard Input:
      python test.py type
      
      Description:
        Demonstrates typing a predefined string by sending individual keystrokes
        
      Note: No parameters required; runs a demo typing sequence
    """
    
    if sys.argv[1] == "mouse":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        x, y = int(x / 100 * 32767), int(y / 100 * 32767)
        move_mouse(ws, x, y)
    elif sys.argv[1] == "scroll":
        if sys.argv[2] == "down":
            scroll_down(ws)
        elif sys.argv[2] == "up":
            scroll_up(ws)
    elif sys.argv[1] == "type":
        type_letter(ws, "h")
        type_letter(ws, "e")
        type_letter(ws, "l")
        type_letter(ws, "l")
        type_letter(ws, "o")
        type_letter(ws, "spc")
        type_letter(ws, "b")
        type_letter(ws, "i")
        type_letter(ws, "t")
        type_letter(ws, "c")
        type_letter(ws, "h")
        type_letter(ws, "spc")
        type_letter(ws, "semicolon", capitalize=True)
        type_letter(ws, "0", capitalize=True)

    time.sleep(0.1)
    view_frame(ws)
