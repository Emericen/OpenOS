from abc import ABC, abstractmethod


class OperatingSystem(ABC):
    @abstractmethod
    def start(self):
        """Start the virtual machine."""
        pass
        
    @abstractmethod
    def stop(self):
        """Stop the virtual machine."""
        pass
        
    @abstractmethod
    def reset(self):
        """Reset the virtual machine."""
        pass
        
    @abstractmethod
    def get_ip(self):
        """Get the IP address of the virtual machine."""
        pass

    @abstractmethod
    def save_state(self):
        pass
