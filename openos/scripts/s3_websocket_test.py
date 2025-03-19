import argparse
from websocket_server import WebsocketServer
import websocket  # pip install websocket-client
import threading


def on_message(client, server, message):
    print(f"[{client['address'][0]}]: {message}")


def on_new_client(client, server):
    print(f"New client connected: {client['address'][0]}")


def on_client_left(client, server):
    print(f"Client disconnected: {client['address'][0]}")


if __name__ == "__main__":

    """
    NOTE: in the following discussion, host refers to the device running VMWare, and guest refers to the VM in VMWare.
    NOTE: in websocket, one server can have many clients, and one client usually corresponds to one server.

    For tests in this script, if Host is server and Guest is client, then:
        On Host run:
            python openos/scripts/s3_websocket_test.py server --ip 0.0.0.0
        On Guest run:
            python openos/scripts/s3_websocket_test.py client --ip 192.168.249.1

    If Host is client and Guest is server, then:
        On Host run:
            python openos/scripts/s3_websocket_test.py client --ip 192.168.249.128
        On Guest run:
            python openos/scripts/s3_websocket_test.py server --ip 0.0.0.0

        NOTE: run `sudo -S ufw allow 8765/tcp` on guest to whitelist inbound tcp traffic.

    NOTE: 192.168.249.1 is host's LAN IP address, and 192.168.249.128 is guest's LAN IP address.
    """

    parser = argparse.ArgumentParser(description="WebSocketTest")
    parser.add_argument(
        "mode", choices=["server", "client"], help="Run as server or client"
    )
    parser.add_argument(
        "--ip",
        default="0.0.0.0",
        help="IP address (server: bind address, client: target address)",
    )
    parser.add_argument("--port", default=8765, type=int, help="Port number")
    args = parser.parse_args()

    try:
        if args.mode == "server":
            server = WebsocketServer(host=args.ip, port=args.port)
            server.set_fn_new_client(on_new_client)
            server.set_fn_client_left(on_client_left)
            server.set_fn_message_received(on_message)
            server.run_forever()
        elif args.mode == "client":
            # Create WebSocket client
            ws = websocket.WebSocketApp(
                f"ws://{args.ip}:{args.port}/",
                on_message=lambda ws, msg: print(f"Received: {msg}"),
                on_error=lambda ws, err: print(f"Error: {err}"),
                on_close=lambda ws, status, msg: print("Connection closed"),
            )

            # Start WebSocket client in a separate thread
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()

            # Send messages from input
            while True:
                message = input("Enter a message: ")
                ws.send(message)
    except KeyboardInterrupt:
        print("Keyboard interrupted. Exiting...")
    finally:
        if args.mode == "client" and "ws" in locals():
            ws.close()
