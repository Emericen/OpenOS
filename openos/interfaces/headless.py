from openos.interfaces.interface import Interface
from openos.host import HostService


class HeadlessInterface(Interface):
    """Headless interface for AI agents."""

    def __init__(self, host: HostService):
        self.host = host
        self.frame_buffer = []
        self.max_buffer_size = 256

    def start(self):
        self.host.start()
        self.running = True

    def run(self):
        if not self.running:
            self.start()

        # Just keep the stream running and buffer frames
        # Agent will call get_frames() and execute_action() separately

    def get_frames(self, count=1):
        frames = []
        for _ in range(count):
            frame = self.host.read_frame()
            if frame is not None:
                self.frame_buffer.append(frame)
                if len(self.frame_buffer) > self.max_buffer_size:
                    self.frame_buffer.pop(0)
                frames.append(frame)
        return frames

    def execute_action(self, action_type, data):
        self.host.send_input(action_type, data)

    def reset(self):
        self.host.reset()

    def stop(self):
        self.running = False
        self.host.stop()
