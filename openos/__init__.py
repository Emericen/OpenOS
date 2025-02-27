from openos.host import HostService
from openos.interfaces import HeadlessInterface, PygameInterface


class OpenOS:
    @staticmethod
    def create(
        interface="headless",
        resolution=(1920, 1080),
        fps=120,
    ):
        """Factory method to create an OpenOS instance with the specified interface."""
        host = HostService(resolution=resolution, fps=fps)

        if interface == "gui":
            return PygameInterface(host)
        elif interface == "headless":
            return HeadlessInterface(host)
        else:
            raise ValueError(f"Unknown interface type: {interface}")


__all__ = ["OpenOS"]
