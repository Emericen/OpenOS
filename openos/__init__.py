from pathlib import Path
from openos.host import HostService
from openos.utils import get_ubuntu_vm_path

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "openos"


class OpenOS:
    @staticmethod
    def create(cache_dir=None):
        if not cache_dir:
            cache_dir = DEFAULT_CACHE_DIR
        else:
            cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_dir, vm_path = get_ubuntu_vm_path(cache_dir=cache_dir)

        host = HostService(cache_dir=cache_dir, vm_path=vm_path)
        return host


__all__ = ["OpenOS"]
