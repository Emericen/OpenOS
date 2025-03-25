import numpy as np
from pathlib import Path

def load_frame_buffer():
    frame_path = Path.home()/'.cache/openos/temp/frame_buffer.dat'
    return np.memmap(
        filename=frame_path,
        dtype=np.uint8,
        mode='r',
        shape=(720, 1280, 4)  # Height, Width, BGRA channels
    )

# Usage:
frame = np.copy(load_frame_buffer())  # Get writable copy
print(frame.shape)