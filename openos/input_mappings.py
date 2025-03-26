import pygame
from pynput import keyboard, mouse
from dataclasses import dataclass
from typing import TypeVar, Optional, Union


@dataclass
class Key:
    name: str
    pygame_key: int
    pynput_key: Union[keyboard.Key, keyboard.KeyCode]


@dataclass
class Button:
    name: str
    pygame_button: int
    pynput_button: mouse.Button


# fmt: off
KEYBOARD_MAPPING = {
    "ESC": Key(name="ESC", pygame_key=pygame.K_ESCAPE, pynput_key=keyboard.Key.esc),
    "ENTER": Key(name="ENTER", pygame_key=pygame.K_RETURN, pynput_key=keyboard.Key.enter),
    "BACKSPACE": Key(name="BACKSPACE", pygame_key=pygame.K_BACKSPACE, pynput_key=keyboard.Key.backspace),
    "TAB": Key(name="TAB", pygame_key=pygame.K_TAB, pynput_key=keyboard.Key.tab),
    "SPACE": Key(name="SPACE", pygame_key=pygame.K_SPACE, pynput_key=keyboard.Key.space),
    "LEFT": Key(name="LEFT", pygame_key=pygame.K_LEFT, pynput_key=keyboard.Key.left),
    "RIGHT": Key(name="RIGHT", pygame_key=pygame.K_RIGHT, pynput_key=keyboard.Key.right),
    "UP": Key(name="UP", pygame_key=pygame.K_UP, pynput_key=keyboard.Key.up),
    "DOWN": Key(name="DOWN", pygame_key=pygame.K_DOWN, pynput_key=keyboard.Key.down),
    "A": Key(name="A", pygame_key=pygame.K_a, pynput_key=keyboard.KeyCode.from_char("a")),
    "B": Key(name="B", pygame_key=pygame.K_b, pynput_key=keyboard.KeyCode.from_char("b")),
    "C": Key(name="C", pygame_key=pygame.K_c, pynput_key=keyboard.KeyCode.from_char("c")),
    "D": Key(name="D", pygame_key=pygame.K_d, pynput_key=keyboard.KeyCode.from_char("d")),
    "E": Key(name="E", pygame_key=pygame.K_e, pynput_key=keyboard.KeyCode.from_char("e")),
    "F": Key(name="F", pygame_key=pygame.K_f, pynput_key=keyboard.KeyCode.from_char("f")),
    "G": Key(name="G", pygame_key=pygame.K_g, pynput_key=keyboard.KeyCode.from_char("g")),
    "H": Key(name="H", pygame_key=pygame.K_h, pynput_key=keyboard.KeyCode.from_char("h")),
    "I": Key(name="I", pygame_key=pygame.K_i, pynput_key=keyboard.KeyCode.from_char("i")),
    "J": Key(name="J", pygame_key=pygame.K_j, pynput_key=keyboard.KeyCode.from_char("j")),
    "K": Key(name="K", pygame_key=pygame.K_k, pynput_key=keyboard.KeyCode.from_char("k")),
    "L": Key(name="L", pygame_key=pygame.K_l, pynput_key=keyboard.KeyCode.from_char("l")),
    "M": Key(name="M", pygame_key=pygame.K_m, pynput_key=keyboard.KeyCode.from_char("m")),
    "N": Key(name="N", pygame_key=pygame.K_n, pynput_key=keyboard.KeyCode.from_char("n")),
    "O": Key(name="O", pygame_key=pygame.K_o, pynput_key=keyboard.KeyCode.from_char("o")),
    "P": Key(name="P", pygame_key=pygame.K_p, pynput_key=keyboard.KeyCode.from_char("p")),
    "Q": Key(name="Q", pygame_key=pygame.K_q, pynput_key=keyboard.KeyCode.from_char("q")),
    "R": Key(name="R", pygame_key=pygame.K_r, pynput_key=keyboard.KeyCode.from_char("r")),
    "S": Key(name="S", pygame_key=pygame.K_s, pynput_key=keyboard.KeyCode.from_char("s")),
    "T": Key(name="T", pygame_key=pygame.K_t, pynput_key=keyboard.KeyCode.from_char("t")),
    "U": Key(name="U", pygame_key=pygame.K_u, pynput_key=keyboard.KeyCode.from_char("u")),
    "V": Key(name="V", pygame_key=pygame.K_v, pynput_key=keyboard.KeyCode.from_char("v")),
    "W": Key(name="W", pygame_key=pygame.K_w, pynput_key=keyboard.KeyCode.from_char("w")),
    "X": Key(name="X", pygame_key=pygame.K_x, pynput_key=keyboard.KeyCode.from_char("x")),
    "Y": Key(name="Y", pygame_key=pygame.K_y, pynput_key=keyboard.KeyCode.from_char("y")),
    "Z": Key(name="Z", pygame_key=pygame.K_z, pynput_key=keyboard.KeyCode.from_char("z")),
    "0": Key(name="0", pygame_key=pygame.K_0, pynput_key=keyboard.KeyCode.from_char("0")),
    "1": Key(name="1", pygame_key=pygame.K_1, pynput_key=keyboard.KeyCode.from_char("1")),
    "2": Key(name="2", pygame_key=pygame.K_2, pynput_key=keyboard.KeyCode.from_char("2")),
    "3": Key(name="3", pygame_key=pygame.K_3, pynput_key=keyboard.KeyCode.from_char("3")),
    "4": Key(name="4", pygame_key=pygame.K_4, pynput_key=keyboard.KeyCode.from_char("4")),
    "5": Key(name="5", pygame_key=pygame.K_5, pynput_key=keyboard.KeyCode.from_char("5")),
    "6": Key(name="6", pygame_key=pygame.K_6, pynput_key=keyboard.KeyCode.from_char("6")),
    "7": Key(name="7", pygame_key=pygame.K_7, pynput_key=keyboard.KeyCode.from_char("7")),
    "8": Key(name="8", pygame_key=pygame.K_8, pynput_key=keyboard.KeyCode.from_char("8")),
    "9": Key(name="9", pygame_key=pygame.K_9, pynput_key=keyboard.KeyCode.from_char("9")),
    "F1": Key(name="F1", pygame_key=pygame.K_F1, pynput_key=keyboard.Key.f1),
    "F2": Key(name="F2", pygame_key=pygame.K_F2, pynput_key=keyboard.Key.f2),
    "F3": Key(name="F3", pygame_key=pygame.K_F3, pynput_key=keyboard.Key.f3),
    "F4": Key(name="F4", pygame_key=pygame.K_F4, pynput_key=keyboard.Key.f4),
    "F5": Key(name="F5", pygame_key=pygame.K_F5, pynput_key=keyboard.Key.f5),
    "F6": Key(name="F6", pygame_key=pygame.K_F6, pynput_key=keyboard.Key.f6),
    "F7": Key(name="F7", pygame_key=pygame.K_F7, pynput_key=keyboard.Key.f7),
    "F8": Key(name="F8", pygame_key=pygame.K_F8, pynput_key=keyboard.Key.f8),
    "F9": Key(name="F9", pygame_key=pygame.K_F9, pynput_key=keyboard.Key.f9),
    "F10": Key(name="F10", pygame_key=pygame.K_F10, pynput_key=keyboard.Key.f10),
    "F11": Key(name="F11", pygame_key=pygame.K_F11, pynput_key=keyboard.Key.f11),
    "F12": Key(name="F12", pygame_key=pygame.K_F12, pynput_key=keyboard.Key.f12),
    "[": Key(name="[", pygame_key=pygame.K_LEFTBRACKET, pynput_key=keyboard.KeyCode.from_char("[")),
    "]": Key(name="]", pygame_key=pygame.K_RIGHTBRACKET, pynput_key=keyboard.KeyCode.from_char("]")),
    "\\": Key(name="\\", pygame_key=pygame.K_BACKSLASH, pynput_key=keyboard.KeyCode.from_char("\\")),
    ";": Key(name=";", pygame_key=pygame.K_SEMICOLON, pynput_key=keyboard.KeyCode.from_char(";")),
    "'": Key(name="'", pygame_key=pygame.K_QUOTE, pynput_key=keyboard.KeyCode.from_char("'")),
    ",": Key(name=",", pygame_key=pygame.K_COMMA, pynput_key=keyboard.KeyCode.from_char(",")),
    ".": Key(name=".", pygame_key=pygame.K_PERIOD, pynput_key=keyboard.KeyCode.from_char(".")),
    "/": Key(name="/", pygame_key=pygame.K_SLASH, pynput_key=keyboard.KeyCode.from_char("/")),
    "`": Key(name="`", pygame_key=pygame.K_BACKQUOTE, pynput_key=keyboard.KeyCode.from_char("`")),
    "(": Key(name="(", pygame_key=pygame.K_LEFTPAREN, pynput_key=keyboard.KeyCode.from_char("(")),
    ")": Key(name=")", pygame_key=pygame.K_RIGHTPAREN, pynput_key=keyboard.KeyCode.from_char(")")),
    "{": Key(name="{", pygame_key=pygame.K_LEFTBRACKET, pynput_key=keyboard.KeyCode.from_char("{")),
    "}": Key(name="}", pygame_key=pygame.K_RIGHTBRACKET, pynput_key=keyboard.KeyCode.from_char("}")),
    "=": Key(name="=", pygame_key=pygame.K_EQUALS, pynput_key=keyboard.KeyCode.from_char("=")),
    "-": Key(name="-", pygame_key=pygame.K_MINUS, pynput_key=keyboard.KeyCode.from_char("-")),
    "_": Key(name="_", pygame_key=pygame.K_UNDERSCORE, pynput_key=keyboard.KeyCode.from_char("_")),
    "+": Key(name="+", pygame_key=pygame.K_PLUS, pynput_key=keyboard.KeyCode.from_char("+")),
    "*": Key(name="*", pygame_key=pygame.K_ASTERISK, pynput_key=keyboard.KeyCode.from_char("*")),
    "#": Key(name="#", pygame_key=pygame.K_HASH, pynput_key=keyboard.KeyCode.from_char("#")),
    "%": Key(name="%", pygame_key=pygame.K_PERCENT, pynput_key=keyboard.KeyCode.from_char("%")),
    "CAPSLOCK": Key(name="CAPSLOCK", pygame_key=pygame.K_CAPSLOCK, pynput_key=keyboard.Key.caps_lock),
    "PRINTSCREEN": Key(name="PRINTSCREEN", pygame_key=pygame.K_PRINTSCREEN, pynput_key=keyboard.Key.print_screen),
    "SCROLLLOCK": Key(name="SCROLLLOCK", pygame_key=pygame.K_SCROLLLOCK, pynput_key=keyboard.Key.scroll_lock),
    "PAUSE": Key(name="PAUSE", pygame_key=pygame.K_PAUSE, pynput_key=keyboard.Key.pause),
    "INSERT": Key(name="INSERT", pygame_key=pygame.K_INSERT, pynput_key=keyboard.Key.insert),
    "DELETE": Key(name="DELETE", pygame_key=pygame.K_DELETE, pynput_key=keyboard.Key.delete),
    "HOME": Key(name="HOME", pygame_key=pygame.K_HOME, pynput_key=keyboard.Key.home),
    "END": Key(name="END", pygame_key=pygame.K_END, pynput_key=keyboard.Key.end),
    "PAGEUP": Key(name="PAGEUP", pygame_key=pygame.K_PAGEUP, pynput_key=keyboard.Key.page_up),
    "PAGEDOWN": Key(name="PAGEDOWN", pygame_key=pygame.K_PAGEDOWN, pynput_key=keyboard.Key.page_down),
    "NUMLOCK": Key(name="NUMLOCK", pygame_key=pygame.K_NUMLOCKCLEAR, pynput_key=keyboard.Key.num_lock),
    "LEFT_CTRL": Key(name="LEFT_CTRL", pygame_key=pygame.K_LCTRL, pynput_key=keyboard.Key.ctrl_l),
    "RIGHT_CTRL": Key(name="RIGHT_CTRL", pygame_key=pygame.K_RCTRL, pynput_key=keyboard.Key.ctrl_r),
    "LEFT_SHIFT": Key(name="LEFT_SHIFT", pygame_key=pygame.K_LSHIFT, pynput_key=keyboard.Key.shift_l),
    "RIGHT_SHIFT": Key(name="RIGHT_SHIFT", pygame_key=pygame.K_RSHIFT, pynput_key=keyboard.Key.shift_r),
    "LEFT_ALT": Key(name="LEFT_ALT", pygame_key=pygame.K_LALT, pynput_key=keyboard.Key.alt_l),
    "RIGHT_ALT": Key(name="RIGHT_ALT", pygame_key=pygame.K_RALT, pynput_key=keyboard.Key.alt_r),
    "LEFT_CMD": Key(name="LEFT_CMD", pygame_key=pygame.K_LGUI, pynput_key=keyboard.Key.cmd_l),
    "RIGHT_CMD": Key(name="RIGHT_CMD", pygame_key=pygame.K_RGUI, pynput_key=keyboard.Key.cmd_r),
}

MOUSE_MAPPING = {
    "LEFT": Button(name="LEFT", pygame_button=pygame.BUTTON_LEFT, pynput_button=mouse.Button.left),
    "RIGHT": Button(name="RIGHT", pygame_button=pygame.BUTTON_RIGHT, pynput_button=mouse.Button.right),
    "MIDDLE": Button(name="MIDDLE", pygame_button=pygame.BUTTON_MIDDLE, pynput_button=mouse.Button.middle),
}
# fmt: on


T = TypeVar("T")


def find_key(
    pygame_key: int = None,
    pynput_key: Union[keyboard.Key, keyboard.KeyCode] = None,
    name: str = None,
) -> Optional[Key]:
    """
    Find a key by pygame_key, pynput_key, or name.

    Args:
        pygame_key: The pygame key code
        pynput_key: The pynput key
        name: The key name

    Returns:
        The key if found, else None
    """
    if pygame_key is None and pynput_key is None and name is None:
        raise ValueError(
            "At least one of pygame_key, pynput_key, or name must be provided"
        )

    # Direct lookup by name (fastest)
    if name is not None:
        return KEYBOARD_MAPPING.get(name)

    # Search by pygame_key or pynput_key
    for key in KEYBOARD_MAPPING.values():
        if pygame_key is not None and key.pygame_key == pygame_key:
            return key
        if pynput_key is not None and key.pynput_key == pynput_key:
            return key

    return None


def find_button(
    pygame_button: int = None,
    pynput_button: mouse.Button = None,
    name: str = None,
) -> Optional[Button]:
    """
    Find a mouse button by pygame_button, pynput_button, or name.

    Args:
        pygame_button: The pygame button code
        pynput_button: The pynput button
        name: The button name

    Returns:
        The button if found, else None
    """
    if pygame_button is None and pynput_button is None and name is None:
        raise ValueError(
            "At least one of pygame_button, pynput_button, or name must be provided"
        )

    # Direct lookup by name (fastest)
    if name is not None:
        return MOUSE_MAPPING.get(name)

    # Search by pygame_button or pynput_button
    for button in MOUSE_MAPPING.values():
        if pygame_button is not None and button.pygame_button == pygame_button:
            return button
        if pynput_button is not None and button.pynput_button == pynput_button:
            return button

    return None


# Example usage:
if __name__ == "__main__":
    print(f"Total keyboard keys: {len(KEYBOARD_MAPPING)}")
    print(f"Total mouse buttons: {len(MOUSE_MAPPING)}")
    print("--------------------------------")
    space_key = find_key(pygame_key=pygame.K_SPACE)
    print(f"> Space key by pygame key: {space_key}")

    enter_key = find_key(name="ENTER")
    print(f"> Enter key by name: {enter_key}")

    a_key = find_key(pynput_key=keyboard.KeyCode.from_char("a"))
    print(f"> A key by pynput key: {a_key}")

    # Looking up mouse buttons
    left_button = find_button(pygame_button=pygame.BUTTON_LEFT)
    print(f"> Left mouse button by pygame button: {left_button}")

    right_button = find_button(name="RIGHT")
    print(f"> Right mouse button by name: {right_button}")

    middle_button = find_button(pynput_button=mouse.Button.middle)
    print(f"> Middle mouse button by pynput button: {middle_button}")
