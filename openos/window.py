import pygame
import sys
from openos.host import HostService


def main(host: HostService):
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode(host._resolution)
    pygame.display.set_caption("OpenOS")
    clock = pygame.time.Clock()

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                host.key_down(event.key)
            elif event.type == pygame.KEYUP:
                host.key_up(event.key)
            elif event.type == pygame.MOUSEMOTION:
                host.position_mouse(*event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                host.button_down(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                host.button_up(event.button)

        # Read and display video frame
        print("reading frame")
        frame = host.read_frame()
        if frame is not None:
            print(frame.shape)
            # Convert numpy array to pygame surface
            surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            screen.blit(surf, (0, 0))
            pygame.display.flip()

        # Cap the frame rate
        clock.tick(120)

    # Cleanup
    pygame.quit()
    host.stop()
    sys.exit()


if __name__ == "__main__":
    try:
        host = HostService()
        host.start()
        main(host)
    except Exception as e:
        print(f"Error: {e}")
        try:
            pygame.quit()
        except:
            pass
        try:
            host.stop()
        except:
            pass
        sys.exit(1)
