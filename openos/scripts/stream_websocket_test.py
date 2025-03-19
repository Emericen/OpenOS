import time
import cv2
import numpy as np
from mss import mss
import zlib
import argparse
import threading
from websocket_server import WebsocketServer
import websocket
import base64


def take_image(sct, area: dict) -> bytes:
    screenshot = sct.grab(area)
    screenshot_array = np.array(screenshot)
    _, jpeg_data = cv2.imencode(
        ".jpg", screenshot_array, [cv2.IMWRITE_JPEG_QUALITY, 80]
    )
    return jpeg_data.tobytes()


def on_new_client(client, server):
    print(f"New client connected: {client['address'][0]}")


def on_client_left(client, server):
    print(f"Client disconnected: {client['address'][0]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", type=str, choices=["sender", "receiver"])
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.mode == "sender":
        # Initialize WebSocket server
        server = WebsocketServer(host="0.0.0.0", port=args.port)
        server.set_fn_new_client(on_new_client)
        server.set_fn_client_left(on_client_left)

        # Start server in a separate thread
        server_thread = threading.Thread(target=server.run_forever)
        server_thread.daemon = True
        server_thread.start()

        print(f"Sender started on port {args.port}, waiting for receivers...")

        with mss() as sct:
            while True:
                if server.clients:
                    img = take_image(
                        sct, area={"left": 0, "top": 0, "width": 1280, "height": 720}
                    )
                    img_compressed = zlib.compress(img)
                    # Convert binary data to base64 string for WebSocket transmission
                    encoded_img = base64.b64encode(img_compressed).decode("utf-8")
                    # Send to all connected clients
                    server.send_message_to_all(encoded_img)
                else:
                    time.sleep(0.1)  # Wait for clients

    elif args.mode == "receiver":
        # Define WebSocket callbacks
        def on_message(ws, message):
            global img_decoded
            # Decode base64 string back to binary
            compressed_data = base64.b64decode(message)
            img_uncompressed = zlib.decompress(compressed_data)
            img_decoded = cv2.imdecode(
                np.frombuffer(img_uncompressed, np.uint8), cv2.IMREAD_COLOR
            )
            cv2.imshow("Stream", img_decoded)
            cv2.waitKey(1)

        def on_error(ws, error):
            print(f"Error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("Connection closed")

        def on_open(ws):
            print("Connection established")

        # Create WebSocket client
        ws = websocket.WebSocketApp(
            f"ws://{args.host}:{args.port}/",
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )

        # Start client
        print(f"Connecting to sender at {args.host}:{args.port}")
        ws.run_forever()
