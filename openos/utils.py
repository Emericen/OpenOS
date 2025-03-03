import platform
from huggingface_hub import hf_hub_download
from pathlib import Path

REPO_ID = "xlangai/ubuntu_osworld"
UBUNTU_ARM_FILENAME = "Ubuntu-arm.zip"
UBUNTU_X86_FILENAME = "Ubuntu-x86.zip"
USER = "eddy"
PASSWORD = "680822dd"

GUEST_OUTPUT_FILE = "/home/eddy/output.txt"
HOST_OUTPUT_FILE = "C:\\Users\\EddyM\\output.txt"

# Create cache directory
CACHE_DIR = Path.home() / ".cache" / "openos"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def install_ubuntu():
    # First check if VM is already unpacked
    vmx_files = list(CACHE_DIR.glob("*.vmx"))
    if vmx_files:
        self.vm_path = str(vmx_files[0])
        print(f"Using existing VM image at {self.vm_path}")
        return self.vm_path

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
    zip_path = hf_hub_download(repo_id=REPO_ID, filename=filename, cache_dir=CACHE_DIR)

    # Extract with subprocess
    print(f"Extracting VM image to {CACHE_DIR}")
    subprocess.run(["unzip", "-o", str(zip_path), "-d", str(CACHE_DIR)])

    # Find the VMX file
    vmx_files = list(CACHE_DIR.glob("*.vmx"))
    self.vm_path = str(vmx_files[0])
    print(f"VM image installed at {self.vm_path}")
    return self.vm_path
