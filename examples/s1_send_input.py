import sys
import time
import websocket


def move_mouse(ws: websocket.WebSocket, x: int, y: int):
    # Convert from percentage to absolute coordinates
    x_abs, y_abs = int(x / 100 * 32767), int(y / 100 * 32767)
    ws.send(f"MOUSE MOVE {x_abs} {y_abs}")


def type_letter(ws: websocket.WebSocket, letter: str, capitalize: bool = False):
    if capitalize:
        ws.send("KEY DOWN SHIFT")
        time.sleep(0.01)
    ws.send(f"KEY DOWN {letter}")
    time.sleep(0.01)
    ws.send(f"KEY UP {letter.upper()}")
    if capitalize:
        ws.send("KEY UP SHIFT")
    time.sleep(0.05)


def scroll_down(ws: websocket.WebSocket):
    ws.send("SCROLL DOWN")
    time.sleep(0.05)


def scroll_up(ws: websocket.WebSocket):
    ws.send("SCROLL UP")
    time.sleep(0.05)


def view_frame(ws: websocket.WebSocket):
    ws.send("SCREENSHOT")


if __name__ == "__main__":

    guest_url = "ws://localhost:8007"
    guest = websocket.WebSocket(enable_multithread=True)
    guest.settimeout(10)
    guest.connect(guest_url, timeout=10)

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
        move_mouse(guest, x, y)
    elif sys.argv[1] == "scroll":
        if sys.argv[2] == "down":
            scroll_down(guest)
        elif sys.argv[2] == "up":
            scroll_up(guest)
    elif sys.argv[1] == "type":
        type_letter(guest, "H", capitalize=True)
        type_letter(guest, "E")
        type_letter(guest, "L")
        type_letter(guest, "L")
        type_letter(guest, "O")
        type_letter(guest, "SPACE")
        type_letter(guest, "B")
        type_letter(guest, "I")
        type_letter(guest, "T")
        type_letter(guest, "C")
        type_letter(guest, "H")
        type_letter(guest, "SPACE")
        type_letter(guest, "SEMICOLON", capitalize=True)
        type_letter(guest, "0", capitalize=True)

    time.sleep(0.1)
    view_frame(guest)
