import pygame
from openos.interfaces.base import BaseInterface

class GUIInterface(BaseInterface):
    """GUI interface using Pygame for human interaction."""
    
    def start(self):
        """Start the OS, connection, and GUI."""
        super().start()
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(self.controller.resolution)
        pygame.display.set_caption("OpenOS")
        
        # Start video stream
        self.stream_handler.start_stream()
        
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
                    self.controller.send_input("keydown", event.key)
                elif event.type == pygame.KEYUP:
                    self.controller.send_input("keyup", event.key)
                elif event.type == pygame.MOUSEMOTION:
                    self.controller.send_input("mousemove", event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.controller.send_input("mousedown", event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.controller.send_input("mouseup", event.button)
            
            # Read and display video frame
            frame = self.stream_handler.read_frame()
            if frame is not None:
                surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.screen.blit(surf, (0, 0))
                pygame.display.flip()
                
        self.stop()
            
    def stop(self):
        """Stop the GUI and OS."""
        self.running = False
        pygame.quit()
        super().stop()
