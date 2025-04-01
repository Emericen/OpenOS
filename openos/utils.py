import os
import platform
import requests
import zipfile
import logging
import colorlog
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


def configure_logger(name, log_file=None, level=logging.INFO):
    logger = logging.getLogger(name)
    
    # Only configure the root openos logger directly
    if name == "openos":
        # Clear existing handlers to avoid duplication
        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
        
        logger.setLevel(level)
        
        # Create formatters and handlers
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(levelname)s %(name)s] %(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        if log_file:
            file_formatter = logging.Formatter(
                "[%(levelname)s %(name)s] %(message)s", 
                datefmt="%H:%M:%S"
            )
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # Disable propagation to avoid root logger duplication
        logger.propagate = False
    
    return logger


def get_ubuntu_vm_path(cache_dir: Path) -> str:
    logger = configure_logger(__name__)

    # First check if VM is already unpacked
    vmx_files = list(cache_dir.glob("**/*.vmx"))
    if vmx_files:
        vm_path = str(vmx_files[0])
        logger.info(f"Using existing VM image at {vm_path}")
        return vm_path

    # Check platform architecture
    machine = platform.machine().lower()
    if machine in ["arm64", "aarch64"]:
        file_url = UBUNTU_ARM_FILE_URL
    elif machine in ["amd64", "x86_64"]:
        file_url = UBUNTU_AMD64_FILE_URL
    else:
        logger.error(f"Unsupported platform or architecture: {machine}")
        raise Exception("Unsupported platform or architecture.")

    # Download corresponding Ubuntu VM image
    logger.info(f"Downloading Ubuntu VM image from {file_url}")
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
    logger.info(f"Extracting VM image to {cache_dir}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file in tqdm(zip_ref.infolist(), desc="Extracting files", unit="file"):
            zip_ref.extract(file, path=cache_dir)

    # Remove the zip file after extraction
    os.remove(zip_path)

    # Find the VMX file (search recursively)
    vmx_files = list(cache_dir.glob("**/*.vmx"))
    vm_path = str(vmx_files[0])
    logger.info(f"VM image installed at {vm_path}")
    return vm_path
