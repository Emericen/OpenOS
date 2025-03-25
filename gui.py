import sys
import pygame
from openos import OpenOS

MOUSE_BUTTON_MAP = {
    pygame.BUTTON_LEFT: "left",
    pygame.BUTTON_MIDDLE: "middle",
    pygame.BUTTON_RIGHT: "right",
}

KEY_MAP = {
    pygame.K_LSHIFT: "shift",
    pygame.K_RSHIFT: "shift",
    pygame.K_LCTRL: "ctrl",
    pygame.K_RCTRL: "ctrl",
    pygame.K_LALT: "alt",
    pygame.K_RALT: "alt",
    pygame.K_SPACE: "space",
    pygame.K_BACKSPACE: "backspace",
    pygame.K_RETURN: "enter",
    pygame.K_TAB: "tab",
    pygame.K_ESCAPE: "esc",
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
    pygame.K_HOME: "home",
    pygame.K_END: "end",
    pygame.K_PAGEUP: "page_up",
    pygame.K_PAGEDOWN: "page_down",
    pygame.K_DELETE: "delete",
    pygame.K_CAPSLOCK: "caps_lock",
    pygame.K_F1: "f1",
    pygame.K_F2: "f2",
    pygame.K_F3: "f3",
    pygame.K_F4: "f4",
    pygame.K_F5: "f5",
    pygame.K_F6: "f6",
    pygame.K_F7: "f7",
    pygame.K_F8: "f8",
    pygame.K_F9: "f9",
    pygame.K_F10: "f10",
    pygame.K_F11: "f11",
    pygame.K_F12: "f12",
}


class OSWindow:
    def __init__(self, host_service, resolution=(1280, 720)):
        self.host = host_service
        self.resolution = resolution
        self._init_pygame()
        self.running = False
        self.mouse_pos = (resolution[0] // 2, resolution[1] // 2)  # Start at center

    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption("OpenOS")
        pygame.event.set_grab(True)  # Capture mouse input
        pygame.mouse.set_visible(False)  # Hide system cursor
        self.clock = pygame.time.Clock()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                self.running = False
            elif event.type == pygame.KEYDOWN:
                print(f"Key down: {event.key}")
                if event.key in KEY_MAP:
                    self.host.keyboard_key_down(KEY_MAP[event.key])
            elif event.type == pygame.KEYUP:
                print(f"Key up: {event.key}")
                if event.key in KEY_MAP:
                    self.host.keyboard_key_up(KEY_MAP[event.key])
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_movement(event.rel)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in MOUSE_BUTTON_MAP:
                    self.host.mouse_button_down(MOUSE_BUTTON_MAP[event.button])
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in MOUSE_BUTTON_MAP:
                    self.host.mouse_button_up(MOUSE_BUTTON_MAP[event.button])

    def _handle_mouse_movement(self, relative_pos):
        dx, dy = relative_pos
        new_x = self.mouse_pos[0] + dx
        new_y = self.mouse_pos[1] + dy
        # Clamp to window boundaries
        self.mouse_pos = (
            max(0, min(new_x, self.resolution[0])),
            max(0, min(new_y, self.resolution[1])),
        )
        try:
            self.host.position_mouse(*self.mouse_pos)
        except Exception as e:
            print(f"Mouse position error: {e}")

    def _render_frame(self):
        frame = self.host.read_frame()
        if frame is not None and frame.shape == (*self.resolution[::-1], 4):
            rgb_frame = frame[..., [2, 1, 0]]  # BGRA to RGB
            surf = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
            self.screen.blit(surf, (0, 0))
        else:
            self.screen.fill((0, 0, 0))  # Fallback black screen

        pygame.display.flip()

    def start(self):
        self.running = True
        while self.running:
            self._handle_events()
            self._render_frame()
            self.clock.tick(60)
        self.stop()

    def stop(self):
        pygame.quit()


def main():
    try:
        host = OpenOS.create(headless=True)
        host.start()
        OSWindow(host).start()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        host.stop()


if __name__ == "__main__":
    main()
