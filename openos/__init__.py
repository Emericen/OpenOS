from pathlib import Path
from openos.host import HostService
from openos.utils import get_ubuntu_vm_path

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "openos"


class OpenOS:
    @staticmethod
    def create(video_port=8765, control_port=8766, cache_dir=None):
        if not cache_dir:
            cache_dir = DEFAULT_CACHE_DIR
        else:
            cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        vm_path = get_ubuntu_vm_path(cache_dir=cache_dir)

        host = HostService(
            vm_path=vm_path, video_port=video_port, control_port=control_port
        )
        return host


__all__ = ["OpenOS"]
