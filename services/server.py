import json
import socket
from websocket_server import WebsocketServer
from services.controller import Controller
from services.log_setup import setup_logging

logging = setup_logging()


class ControlServer:
    def __init__(self):
        self.host, self.port = "0.0.0.0", 8007

        self.server = WebsocketServer(host=self.host, port=self.port)
        self.server.set_fn_new_client(self.on_new_client)
        self.server.set_fn_client_left(self.on_client_left)
        self.server.set_fn_message_received(self.on_message_received)

        self.controller = Controller()

    def on_new_client(self, client, server):
        hostname = socket.gethostname()
        server.send_message(client, f"Hello from {hostname}")
        logging.info(f"New client connected with id: {client['id']}")

    def on_client_left(self, client, server):
        logging.info(f"Client with id: {client['id']} left")

    def on_message_received(self, client, server, message):
        # Convert string message to json
        try:
            message_json = json.loads(message)
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON: {message}")
            server.send_message(
                client,
                json.dumps({"error": "Invalid JSON format", "raw_message": message}),
            )
            return

        # Ensure required keys are present in the message json
        if "type" not in message_json or "data" not in message_json:
            logging.error(f"Missing 'type' or 'data' in JSON: {message_json}")
            server.send_message(
                client,
                json.dumps({"error": "Message must contain 'type' and 'data' fields"}),
            )
            return

        message_type, message_data = message_json["type"], message_json["data"]

        # Handle debug messages
        if message_type == "debug":
            logging.debug(message_data)

        # Handle controller actions / perform valid actions on guest VM
        elif message_type in self.controller.actions:
            self.controller.actions[message_type](**message_data)
        else:
            logging.error(f"Unknown message type: {message_type}")

    def run(self):
        logging.info(f"Websocket server started on {self.host}:{self.port}")
        self.server.run_forever()


if __name__ == "__main__":
    server = ControlServer()
    server.run()
