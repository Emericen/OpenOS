import os
import platform
import requests
import zipfile
from pathlib import Path
from tqdm import tqdm

UBUNTU_AMD64_FILE_URL = (
    "https://huggingface.co/datasets/iiTzEddy/OpenOS/resolve/main/ubuntu-amd.zip"
)
UBUNTU_ARM_FILE_URL = (
    "https://huggingface.co/datasets/iiTzEddy/OpenOS/resolve/main/ubuntu-arm.zip"
)

USER = "user"
PASSWORD = "password"
SHARED_FOLDER_NAME = "temp"

def get_ubuntu_vm_path(cache_dir: Path) -> str:
    # First check if VM is already unpacked
    vmx_files = list(cache_dir.glob("**/*.vmx"))
    if vmx_files:
        vm_path = str(vmx_files[0])
        print(f"Using existing VM image at {vm_path}")
        return vm_path

    # Check platform architecture
    machine = platform.machine().lower()
    if machine in ["arm64", "aarch64"]:
        file_url = UBUNTU_ARM_FILE_URL
    elif machine in ["amd64", "x86_64"]:
        file_url = UBUNTU_AMD64_FILE_URL
    else:
        raise Exception("Unsupported platform or architecture.")

    # Download corresponding Ubuntu VM image
    print(f"Downloading Ubuntu VM image from {file_url}")
    filename = os.path.basename(file_url)
    zip_path = cache_dir / filename
    response = requests.get(file_url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))
    with open(zip_path, "wb") as f:
        with tqdm(total=total_size, unit="B", unit_scale=True, desc=filename) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

    # Extract ZIP file using Python's zipfile module (cross-platform)
    print(f"Extracting VM image to {cache_dir}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file in tqdm(zip_ref.infolist(), desc="Extracting files", unit="file"):
            zip_ref.extract(file, path=cache_dir)

    # Remove the zip file after extraction
    os.remove(zip_path)

    # Find the VMX file (search recursively)
    vmx_files = list(cache_dir.glob("**/*.vmx"))
    vm_path = str(vmx_files[0])
    print(f"VM image installed at {vm_path}")
    return vm_path
