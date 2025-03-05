import platform
import subprocess
from pathlib import Path
from huggingface_hub import hf_hub_download

REPO_ID = "iiTzEddy/OpenOS"
UBUNTU_ARM_FILENAME = "ubuntu-arm.zip"
UBUNTU_X86_FILENAME = "ubuntu-x86.zip"

USER = "Agent"
PASSWORD = "visible-testbed"


def get_ubuntu_vm_path(cache_dir: Path) -> str:
    # First check if VM is already unpacked
    vmx_files = list(cache_dir.glob("*.vmx"))
    if vmx_files:
        vm_path = str(vmx_files[0])
        print(f"Using existing VM image at {vm_path}")
        return vm_path

    # Check platform architecture
    machine = platform.machine().lower()
    if machine in ["arm64", "aarch64"]:
        filename = UBUNTU_ARM_FILENAME
    elif machine in ["amd64", "x86_64"]:
        filename = UBUNTU_X86_FILENAME
    else:
        raise Exception("Unsupported platform or architecture.")

    # Download using huggingface_hub
    print(f"Downloading Ubuntu VM image from {REPO_ID}")
    zip_path = hf_hub_download(repo_id=REPO_ID, filename=filename, cache_dir=cache_dir)

    # Extract with subprocess
    print(f"Extracting VM image to {cache_dir}")
    subprocess.run(["unzip", "-o", str(zip_path), "-d", str(cache_dir)])

    # Find the VMX file
    vmx_files = list(cache_dir.glob("*.vmx"))
    vm_path = str(vmx_files[0])
    print(f"VM image installed at {vm_path}")
    return vm_path


if __name__ == "__main__":
    path = get_ubuntu_vm_path()
    print(path)
