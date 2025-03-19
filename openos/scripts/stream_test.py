import time
import cv2
import numpy as np
from mss import mss
import zlib
import socket
import argparse


def take_image(sct, area: dict) -> bytes:
    screenshot = sct.grab(area)
    screenshot_array = np.array(screenshot)
    _, jpeg_data = cv2.imencode(
        ".jpg", screenshot_array, [cv2.IMWRITE_JPEG_QUALITY, 80]
    )
    return jpeg_data.tobytes()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", type=str, choices=["sender", "receiver"])
    parser.add_argument("target", type=str, default="192.168.1.76")
    parser.add_argument("bind", type=str, default="0.0.0.0")
    parser.add_argument("port", type=int, default=8765)
    args = parser.parse_args()

    target_address = (args.target, args.port)
    bind_address = (args.bind, args.port)

    node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if args.mode == "sender":
        while True:
            try:
                node.connect(target_address)
                break
            except ConnectionRefusedError:
                print("Waiting for receiver...")
                time.sleep(1)
        with mss() as sct:
            while True:
                img = take_image(
                    sct, area={"left": 0, "top": 0, "width": 1280, "height": 720}
                )
                img_compressed = zlib.compress(img)
                # size_in_mb = len(img_compressed) / (1024 * 1024)
                # print(f"Compressed image size: {size_in_mb:.2f} MB")
                msg_size = len(img_compressed).to_bytes(4, 'big')  # 4 bytes for size
                node.sendall(msg_size + img_compressed)  # Using sendall instead of send

    elif args.mode == "receiver":
        node.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
        node.bind(('0.0.0.0', args.port))
        node.listen()
        print("Waiting for sender...")
        conn, addr = node.accept()
        while True:
            msg_size = int.from_bytes(conn.recv(4), 'big')  # Read size first
            data = conn.recv(msg_size)
            img_uncompressed = zlib.decompress(data)
            img_decoded = cv2.imdecode(
                np.frombuffer(img_uncompressed, np.uint8), cv2.IMREAD_COLOR
            )
            cv2.imshow('Stream', img_decoded)
            cv2.waitKey(1)
