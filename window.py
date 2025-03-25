import sys
import pygame
from openos import OpenOS

class OSWindow:
    def __init__(self, host_service):
        self.host = host_service
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720)) # Hardcoded for now
        pygame.display.set_caption("OpenOS")
        self.clock = pygame.time.Clock()
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.host.keyboard_key_down(event.key)
                elif event.type == pygame.KEYUP:
                    self.host.keyboard_key_up(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    self.host.position_mouse(*event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.host.mouse_button_down(event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.host.mouse_button_up(event.button)

            # Read and display video frame
            frame = self.host.read_frame()
            if frame is not None:
                try:
                    # Convert BGRA to RGBA and swap axes
                    rgb_frame = frame[..., [2, 1, 0, 3]]  # Swap BGR to RGB
                    surf = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
                    self.screen.blit(surf, (0, 0))
                    pygame.display.flip()
                except Exception as e:
                    print(f"Frame error: {e}")

            # Cap the frame rate
            self.clock.tick(60)
        
        self.stop()

    def stop(self):
        pygame.quit()


def main():
    
    try:
        host = OpenOS.create(headless=True)
        host.start()
        window = OSWindow(host)
        window.start()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        try:
            host.stop()
        except:
            pass


if __name__ == "__main__":
    main()
