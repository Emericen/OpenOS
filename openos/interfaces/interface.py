from abc import ABC, abstractmethod


class Interface(ABC):
    """Base interface for interacting with OpenOS."""

    @abstractmethod
    def start(self):
        """Start the OS and connection."""
        pass

    @abstractmethod
    def stop(self):
        """Stop the OS and connection."""
        pass

    @abstractmethod
    def reset(self):
        """Reset the OS."""
        pass

    @abstractmethod
    def run(self):
        """Run the interface main loop."""
        pass
