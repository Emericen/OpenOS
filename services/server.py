import json
import socket
import re
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

        # Define command patterns for text-based protocol
        self.command_patterns = {
            r"^MOUSE\s+MOVE\s+(\d+)\s+(\d+)$": self.controller.handle_mouse_move,
            r"^MOUSE\s+DOWN\s+([A-Z]+)$": self.controller.handle_mouse_down,
            r"^MOUSE\s+UP\s+([A-Z]+)$": self.controller.handle_mouse_up,
            r"^SCROLL\s+([A-Z]+)$": self.controller.handle_scroll,
            r"^KEY\s+DOWN\s+([A-Z0-9_]+)$": self.controller.handle_key_down,
            r"^KEY\s+UP\s+([A-Z0-9_]+)$": self.controller.handle_key_up,
            r"^SCREENSHOT(?:\s+(.+))?$": self.controller.handle_screenshot,
        }

    def on_new_client(self, client, server):
        hostname = socket.gethostname()
        server.send_message(client, f"Hello from {hostname}")
        logging.info(f"New client connected with id: {client['id']}")

    def on_client_left(self, client, server):
        logging.info(f"Client with id: {client['id']} left")

    def on_message_received(self, client, server, message):
        logging.debug(f"[{client['id']}] {message}")

        # Process the command
        success, error_msg = self.process_command(message.upper())

        if not success:
            logging.error(error_msg)
            server.send_message(
                client,
                json.dumps({"error": error_msg, "raw_message": message}),
            )

    def process_command(self, command):
        """Process a text command and execute the appropriate action"""
        for pattern, handler in self.command_patterns.items():
            match = re.match(pattern, command)
            if match:
                try:
                    return handler(*match.groups())
                except Exception as e:
                    error_msg = f"Error executing command: {command}. Error: {str(e)}"
                    logging.error(error_msg)
                    return False, error_msg

        return False, f"Unknown command format: {command}"

    def run(self):
        logging.info(f"Websocket server started on {self.host}:{self.port}")
        self.server.run_forever()


if __name__ == "__main__":
    server = ControlServer()
    server.run()
