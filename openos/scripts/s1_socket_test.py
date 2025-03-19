import socket
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SocketTest")
    parser.add_argument(
        "mode", choices=["listener", "sender"], help="Run as listener or sender"
    )
    parser.add_argument("target", default="255.255.255.255", help="Target address")
    parser.add_argument("bind", default="0.0.0.0", help="Bind address")
    parser.add_argument("port", default=8765, type=int, help="Port number")
    args = parser.parse_args()

    try:
        TARGET_ADDRESS = (args.target, args.port)
        BIND_ADDRESS = (args.bind, args.port)

        node = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        node.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        node.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        node.bind(BIND_ADDRESS)

        if args.mode == "listener":
            while True:
                data, addr = node.recvfrom(1024)
                message = data.decode()
                print(f"[{addr[0]}]: {message}")
        elif args.mode == "sender":
            while True:
                message = input("Enter a message: ")
                node.sendto(message.encode(), TARGET_ADDRESS)
    except KeyboardInterrupt:
        print("Keyboard interrupted. Exiting...")
    finally:
        node.close()
