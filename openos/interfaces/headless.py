from openos.interfaces.base import BaseInterface


class HeadlessInterface(BaseInterface):
    """Headless interface for AI agents."""

    def __init__(self, controller):
        super().__init__(controller)
        self.frame_buffer = []
        self.max_buffer_size = 256  # Default max frames to store

    def start(self):
        """Start the OS and connection."""
        super().start()
        self.stream_handler.start_stream()
        self.running = True

    def run(self):
        """Run the headless interface."""
        if not self.running:
            self.start()

        # Just keep the stream running and buffer frames
        # Agent will call get_frames() and execute_action() separately

    def get_frames(self, count=1):
        """Get the latest frames from the buffer.

        Args:
            count: Number of frames to return

        Returns:
            List of frames as numpy arrays
        """
        frames = []
        for _ in range(count):
            frame = self.stream_handler.read_frame()
            if frame is not None:
                self.frame_buffer.append(frame)
                # Maintain buffer size
                if len(self.frame_buffer) > self.max_buffer_size:
                    self.frame_buffer.pop(0)
                frames.append(frame)

        return frames

    def execute_action(self, action_type, data):
        """Execute an action in the VM.

        Args:
            action_type: Type of action (keydown, mousemove, etc.)
            data: Action data
        """
        self.controller.send_input(action_type, data)

    def stop(self):
        """Stop the headless interface and OS."""
        self.running = False
        super().stop()
