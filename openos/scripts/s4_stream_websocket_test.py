import argparse
from websocket_server import WebsocketServer
import websocket  # pip install websocket-client
import threading
import time


if __name__ == "__main__":

    """
    NOTE: in the following discussion, host refers to the device running VMWare, and guest refers to the VM in VMWare.

    If Host is server and Guest is client, then:
        On Host run:
            python openos/scripts/s4_stream_websocket_test.py server --ip 0.0.0.0
        On Guest run:
            python openos/scripts/s4_stream_websocket_test.py client --ip 192.168.249.1
    If Guest is server and Host is client, then:
        On Guest run:
            python openos/scripts/s4_stream_websocket_test.py server --ip 0.0.0.0
        On Host run:
            python openos/scripts/s4_stream_websocket_test.py client --ip 192.168.249.128

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

            def on_message(client, server, message):
                print(f"[{client['address'][0]}]: {message}")

            def on_new_client(client, server):
                print(f"New client connected: {client['address'][0]}")

            def on_client_left(client, server):
                print(f"Client disconnected: {client['address'][0]}")

            server = WebsocketServer(host=args.ip, port=args.port)
            server.set_fn_new_client(on_new_client)
            server.set_fn_client_left(on_client_left)
            server.set_fn_message_received(on_message)
            server_thread = threading.Thread(target=server.run_forever)
            server_thread.daemon = True
            server_thread.start()

            number = 0
            while True:
                if server.clients:
                    number += 1
                    print(f"Sending: {number}")
                    server.send_message_to_all(str(number))
                    number = number % (2**32)
                    time.sleep(0.01)
                else:
                    print("No clients connected, waiting...")
                    time.sleep(5)

        elif args.mode == "client":

            def on_message(ws, message):
                print(f"Received: {message}")

            def on_error(ws, error):
                print(f"Error: {error}")

            def on_close(ws, status, msg):
                print("Connection closed")

            # Create WebSocket client
            ws = websocket.WebSocketApp(
                f"ws://{args.ip}:{args.port}/",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )

            # Start WebSocket client in a separate thread
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()

            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("Keyboard interrupted. Exiting...")
    finally:
        if args.mode == "client" and "ws" in locals():
            ws.close()
        if args.mode == "server" and "server" in locals():
            server.shutdown()
