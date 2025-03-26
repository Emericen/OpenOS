import cv2
import pygame
from openos import OpenOS, find_key, find_button

RESOLUTION = (1280, 720)


class GUI:
    def __init__(self):
        self.ubuntu_vm = OpenOS.create(headless=True)
        pygame.init()
        pygame.event.set_grab(True)
        self.screen = pygame.display.set_mode(size=RESOLUTION)
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        self.ubuntu_vm.start()
        try:
            while self.running:
                self._handle_display()
                self._handle_input()
                self.clock.tick(60)
        except KeyboardInterrupt:
            print("Keyboard interrupt")
        finally:
            self.ubuntu_vm.stop()
            pygame.quit()

    def _handle_display(self):
        frame = self.ubuntu_vm.read_frame()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        frame = frame.transpose(1, 0, 2)
        pygame.surfarray.blit_array(self.screen, frame)
        pygame.display.flip()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                key = find_key(pygame_key=event.key)
                if key:
                    self.ubuntu_vm.keyboard_key_down(key.name)

            elif event.type == pygame.KEYUP:
                key = find_key(pygame_key=event.key)
                if key:
                    self.ubuntu_vm.keyboard_key_up(key.name)

            elif event.type == pygame.MOUSEMOTION:
                self.ubuntu_vm.move_mouse(event.rel[0], event.rel[1])

            elif event.type == pygame.MOUSEBUTTONDOWN:
                button = find_button(pygame_button=event.button)
                if button:
                    self.ubuntu_vm.mouse_button_down(button.name)
            elif event.type == pygame.MOUSEBUTTONUP:
                button = find_button(pygame_button=event.button)
                if button:
                    self.ubuntu_vm.mouse_button_up(button.name)

            elif event.type == pygame.MOUSEWHEEL:
                self.ubuntu_vm.scroll(event.x, event.y)

if __name__ == "__main__":
    GUI().run()
