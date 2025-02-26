from abc import ABC, abstractmethod
from openos.core.controller import Controller
from openos.core.receiver import Receiver

class BaseInterface(ABC):
    """Base interface for interacting with OpenOS."""
    
    def __init__(self, controller: Controller):
        self.controller = controller
        self.receiver = None
        
    def start(self):
        """Start the OS and connection."""
        server_ip = self.controller.start()
        self.receiver = Receiver(
            server_ip,
            self.controller.server_port,
            self.controller.resolution
        )
        
    def stop(self):
        """Stop the OS and connection."""
        if self.receiver:
            self.receiver.stop_stream()
        self.controller.stop()
        
    def reset(self):
        """Reset the OS."""
        self.controller.reset()
        
    @abstractmethod
    def run(self):
        """Run the interface main loop."""
        pass
