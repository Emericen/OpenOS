from pathlib import Path
from openos.host import HostService
from openos.utils import get_ubuntu_vm_path, USER, PASSWORD, SHARED_FOLDER_NAME
from openos.input_mappings import find_key, find_button

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "openos"


class OpenOS:
    @staticmethod
    def create(cache_dir=None, headless=False):
        if not cache_dir:
            cache_dir = DEFAULT_CACHE_DIR
        else:
            cache_dir = Path(cache_dir)

        cache_dir.mkdir(parents=True, exist_ok=True)
        vm_path = get_ubuntu_vm_path(cache_dir=cache_dir)
        return HostService(cache_dir=cache_dir, vm_path=vm_path, headless=headless)


__all__ = ["OpenOS", "find_key", "find_button"]
