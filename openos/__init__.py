from pathlib import Path
import logging
from openos.host import HostService
from openos.utils import get_ubuntu_vm_path, configure_logger

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "openos"


class OpenOS:
    @staticmethod
    def create(cache_dir=None, debug=False):
        if not cache_dir:
            cache_dir = DEFAULT_CACHE_DIR
        else:
            cache_dir = Path(cache_dir)

        if debug:
            configure_logger("openos", level=logging.DEBUG)
        else:
            configure_logger("openos", level=logging.INFO)

        cache_dir.mkdir(parents=True, exist_ok=True)
        vm_path = get_ubuntu_vm_path(cache_dir=cache_dir)
        return HostService(cache_dir=cache_dir, vm_path=vm_path)


__all__ = ["OpenOS"]
