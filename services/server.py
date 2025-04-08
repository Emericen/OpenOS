import sys
import logging
from websocket_server import WebsocketServer

LOGGING_FMT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.INFO, stream=sys.stdout, format=LOGGING_FMT, force=True
)


class VMGatewayServer:
    def __init__(self, host="0.0.0.0", port=8007):
        self.server = WebsocketServer(host, port)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)

    def new_client(self, client, server):
        logging.info("New client connected")

    def client_left(self, client, server):
        logging.info("Client disconnected")

    def message_received(self, client, server, message):
        logging.info(f"Message received: {message}")

    def run(self):
        logging.info("Starting WebSocket server...")
        self.server.run_forever()


if __name__ == "__main__":
    logging.info("Starting VMGatewayServer...")
    server = VMGatewayServer()
    server.run()
