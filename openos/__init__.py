from openos.core.controller import Controller
from openos.interfaces.gui import GUIInterface
from openos.interfaces.headless import HeadlessInterface
from openos.providers import VMWare, VirtualBox, Docker


class OpenOS:
    @staticmethod
    def create(
        os_type="ubuntu",
        interface="gui",
        vm_path=None,
        resolution=(1920, 1080),
        fps=120,
    ):
        """Factory method to create an OpenOS instance with the specified interface."""
        controller = Controller(
            os_type=os_type, vm_path=vm_path, resolution=resolution, fps=fps
        )

        if interface == "gui":
            return GUIInterface(controller)
        elif interface == "headless":
            return HeadlessInterface(controller)
        else:
            raise ValueError(f"Unknown interface type: {interface}")


__all__ = ["OpenOS", "VMWare", "VirtualBox", "Docker"]
