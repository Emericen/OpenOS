from openos.host import HostService
from openos.pygame import PygameInterface


class OpenOS:
    @staticmethod
    def create(video_port=8765, control_port=8766, human_player=False, cache_dir=None):
        """Factory method to create an OpenOS instance with the specified interface."""
        host = HostService(
            video_port=video_port, control_port=control_port, cache_dir=cache_dir
        )

        if human_player:
            return PygameInterface(host)
        else:
            return host


__all__ = ["OpenOS"]
