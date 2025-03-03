import openos.pygame as pygame
from openos.host import HostService

class PygameInterface:
    """Interface using Pygame for human interaction."""

    def __init__(self, host: HostService):
        self.host = host
        self.screen = None
        self.running = False

    def start(self):
        """Start the OS, connection, and GUI."""

        self.host.start()

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(self.host.resolution)
        pygame.display.set_caption("OpenOS")

        # Start main loop automatically
        self.running = True

    def run(self):
        """Run the pygame main loop."""
        if not self.running:
            self.start()

        while self.running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.host.send_input("keydown", event.key)
                elif event.type == pygame.KEYUP:
                    self.host.send_input("keyup", event.key)
                elif event.type == pygame.MOUSEMOTION:
                    self.host.send_input("mousemove", event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.host.send_input("mousedown", event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.host.send_input("mouseup", event.button)

            # Read and display video frame
            frame = self.host.read_frame()
            if frame is not None:
                surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.screen.blit(surf, (0, 0))
                pygame.display.flip()

        self.stop()

    def reset(self):
        """Reset the GUI and OS."""
        self.host.reset()

    def stop(self):
        """Stop the GUI and OS."""
        self.running = False
        pygame.quit()
        super().stop()
