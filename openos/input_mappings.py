from pynput import keyboard, mouse
from dataclasses import dataclass
from typing import TypeVar, Optional, Union


@dataclass
class Key:
    name: str
    pynput_key: Union[keyboard.Key, keyboard.KeyCode]


@dataclass
class Button:
    name: str
    pynput_button: mouse.Button


KEYBOARD_MAPPING = {
    "ESC": Key(name="ESC", pynput_key=keyboard.Key.esc),
    "ENTER": Key(name="ENTER", pynput_key=keyboard.Key.enter),
    "BACKSPACE": Key(name="BACKSPACE", pynput_key=keyboard.Key.backspace),
    "TAB": Key(name="TAB", pynput_key=keyboard.Key.tab),
    "SPACE": Key(name="SPACE", pynput_key=keyboard.Key.space),
    "LEFT": Key(name="LEFT", pynput_key=keyboard.Key.left),
    "RIGHT": Key(name="RIGHT", pynput_key=keyboard.Key.right),
    "UP": Key(name="UP", pynput_key=keyboard.Key.up),
    "DOWN": Key(name="DOWN", pynput_key=keyboard.Key.down),
    "A": Key(name="A", pynput_key=keyboard.KeyCode.from_char("a")),
    "B": Key(name="B", pynput_key=keyboard.KeyCode.from_char("b")),
    "C": Key(name="C", pynput_key=keyboard.KeyCode.from_char("c")),
    "D": Key(name="D", pynput_key=keyboard.KeyCode.from_char("d")),
    "E": Key(name="E", pynput_key=keyboard.KeyCode.from_char("e")),
    "F": Key(name="F", pynput_key=keyboard.KeyCode.from_char("f")),
    "G": Key(name="G", pynput_key=keyboard.KeyCode.from_char("g")),
    "H": Key(name="H", pynput_key=keyboard.KeyCode.from_char("h")),
    "I": Key(name="I", pynput_key=keyboard.KeyCode.from_char("i")),
    "J": Key(name="J", pynput_key=keyboard.KeyCode.from_char("j")),
    "K": Key(name="K", pynput_key=keyboard.KeyCode.from_char("k")),
    "L": Key(name="L", pynput_key=keyboard.KeyCode.from_char("l")),
    "M": Key(name="M", pynput_key=keyboard.KeyCode.from_char("m")),
    "N": Key(name="N", pynput_key=keyboard.KeyCode.from_char("n")),
    "O": Key(name="O", pynput_key=keyboard.KeyCode.from_char("o")),
    "P": Key(name="P", pynput_key=keyboard.KeyCode.from_char("p")),
    "Q": Key(name="Q", pynput_key=keyboard.KeyCode.from_char("q")),
    "R": Key(name="R", pynput_key=keyboard.KeyCode.from_char("r")),
    "S": Key(name="S", pynput_key=keyboard.KeyCode.from_char("s")),
    "T": Key(name="T", pynput_key=keyboard.KeyCode.from_char("t")),
    "U": Key(name="U", pynput_key=keyboard.KeyCode.from_char("u")),
    "V": Key(name="V", pynput_key=keyboard.KeyCode.from_char("v")),
    "W": Key(name="W", pynput_key=keyboard.KeyCode.from_char("w")),
    "X": Key(name="X", pynput_key=keyboard.KeyCode.from_char("x")),
    "Y": Key(name="Y", pynput_key=keyboard.KeyCode.from_char("y")),
    "Z": Key(name="Z", pynput_key=keyboard.KeyCode.from_char("z")),
    "0": Key(name="0", pynput_key=keyboard.KeyCode.from_char("0")),
    "1": Key(name="1", pynput_key=keyboard.KeyCode.from_char("1")),
    "2": Key(name="2", pynput_key=keyboard.KeyCode.from_char("2")),
    "3": Key(name="3", pynput_key=keyboard.KeyCode.from_char("3")),
    "4": Key(name="4", pynput_key=keyboard.KeyCode.from_char("4")),
    "5": Key(name="5", pynput_key=keyboard.KeyCode.from_char("5")),
    "6": Key(name="6", pynput_key=keyboard.KeyCode.from_char("6")),
    "7": Key(name="7", pynput_key=keyboard.KeyCode.from_char("7")),
    "8": Key(name="8", pynput_key=keyboard.KeyCode.from_char("8")),
    "9": Key(name="9", pynput_key=keyboard.KeyCode.from_char("9")),
    "F1": Key(name="F1", pynput_key=keyboard.Key.f1),
    "F2": Key(name="F2", pynput_key=keyboard.Key.f2),
    "F3": Key(name="F3", pynput_key=keyboard.Key.f3),
    "F4": Key(name="F4", pynput_key=keyboard.Key.f4),
    "F5": Key(name="F5", pynput_key=keyboard.Key.f5),
    "F6": Key(name="F6", pynput_key=keyboard.Key.f6),
    "F7": Key(name="F7", pynput_key=keyboard.Key.f7),
    "F8": Key(name="F8", pynput_key=keyboard.Key.f8),
    "F9": Key(name="F9", pynput_key=keyboard.Key.f9),
    "F10": Key(name="F10", pynput_key=keyboard.Key.f10),
    "F11": Key(name="F11", pynput_key=keyboard.Key.f11),
    "F12": Key(name="F12", pynput_key=keyboard.Key.f12),
    "[": Key(name="[", pynput_key=keyboard.KeyCode.from_char("[")),
    "]": Key(name="]", pynput_key=keyboard.KeyCode.from_char("]")),
    "\\": Key(name="\\", pynput_key=keyboard.KeyCode.from_char("\\")),
    ";": Key(name=";", pynput_key=keyboard.KeyCode.from_char(";")),
    "'": Key(name="'", pynput_key=keyboard.KeyCode.from_char("'")),
    ",": Key(name=",", pynput_key=keyboard.KeyCode.from_char(",")),
    ".": Key(name=".", pynput_key=keyboard.KeyCode.from_char(".")),
    "/": Key(name="/", pynput_key=keyboard.KeyCode.from_char("/")),
    "`": Key(name="`", pynput_key=keyboard.KeyCode.from_char("`")),
    "(": Key(name="(", pynput_key=keyboard.KeyCode.from_char("(")),
    ")": Key(name=")", pynput_key=keyboard.KeyCode.from_char(")")),
    "{": Key(name="{", pynput_key=keyboard.KeyCode.from_char("{")),
    "}": Key(name="}", pynput_key=keyboard.KeyCode.from_char("}")),
    "=": Key(name="=", pynput_key=keyboard.KeyCode.from_char("=")),
    "-": Key(name="-", pynput_key=keyboard.KeyCode.from_char("-")),
    "_": Key(name="_", pynput_key=keyboard.KeyCode.from_char("_")),
    "+": Key(name="+", pynput_key=keyboard.KeyCode.from_char("+")),
    "*": Key(name="*", pynput_key=keyboard.KeyCode.from_char("*")),
    "#": Key(name="#", pynput_key=keyboard.KeyCode.from_char("#")),
    "%": Key(name="%", pynput_key=keyboard.KeyCode.from_char("%")),
    "CAPSLOCK": Key(name="CAPSLOCK", pynput_key=keyboard.Key.caps_lock),
    "DELETE": Key(name="DELETE", pynput_key=keyboard.Key.delete),
    "HOME": Key(name="HOME", pynput_key=keyboard.Key.home),
    "END": Key(name="END", pynput_key=keyboard.Key.end),
    "PAGEUP": Key(name="PAGEUP", pynput_key=keyboard.Key.page_up),
    "PAGEDOWN": Key(name="PAGEDOWN", pynput_key=keyboard.Key.page_down),
    "LEFT_CTRL": Key(name="LEFT_CTRL", pynput_key=keyboard.Key.ctrl_l),
    "RIGHT_CTRL": Key(name="RIGHT_CTRL", pynput_key=keyboard.Key.ctrl_r),
    "LEFT_SHIFT": Key(name="LEFT_SHIFT", pynput_key=keyboard.Key.shift_l),
    "RIGHT_SHIFT": Key(name="RIGHT_SHIFT", pynput_key=keyboard.Key.shift_r),
    "LEFT_ALT": Key(name="LEFT_ALT", pynput_key=keyboard.Key.alt_l),
    "RIGHT_ALT": Key(name="RIGHT_ALT", pynput_key=keyboard.Key.alt_r),
    "LEFT_CMD": Key(name="LEFT_CMD", pynput_key=keyboard.Key.cmd_l),
    "RIGHT_CMD": Key(name="RIGHT_CMD", pynput_key=keyboard.Key.cmd_r),
}

MOUSE_MAPPING = {
    "LEFT": Button(name="LEFT", pynput_button=mouse.Button.left),
    "RIGHT": Button(name="RIGHT", pynput_button=mouse.Button.right),
    "MIDDLE": Button(name="MIDDLE", pynput_button=mouse.Button.middle),
}


T = TypeVar("T")


def find_key(
    pynput_key: Union[keyboard.Key, keyboard.KeyCode] = None,
    name: str = None,
) -> Optional[Key]:
    """
    Find a key by pynput_key or name.

    Args:
        pynput_key: The pynput key
        name: The key name

    Returns:
        The key if found, else None
    """
    if pynput_key is None and name is None:
        raise ValueError("At least one of pynput_key or name must be provided")

    # Direct lookup by name (fastest)
    if name is not None:
        return KEYBOARD_MAPPING.get(name)

    # Search by pynput_key
    for key in KEYBOARD_MAPPING.values():
        if pynput_key is not None and key.pynput_key == pynput_key:
            return key

    return None


def find_button(
    pynput_button: mouse.Button = None,
    name: str = None,
) -> Optional[Button]:
    """
    Find a mouse button by pynput_button or name.

    Args:
        pynput_button: The pynput button
        name: The button name

    Returns:
        The button if found, else None
    """
    if pynput_button is None and name is None:
        raise ValueError("At least one of pynput_button or name must be provided")

    # Direct lookup by name (fastest)
    if name is not None:
        return MOUSE_MAPPING.get(name)

    # Search by pynput_button
    for button in MOUSE_MAPPING.values():
        if pynput_button is not None and button.pynput_button == pynput_button:
            return button

    return None


# Example usage:
if __name__ == "__main__":
    print(f"Total keyboard keys: {len(KEYBOARD_MAPPING)}")
    print(f"Total mouse buttons: {len(MOUSE_MAPPING)}")
    print("--------------------------------")

    enter_key = find_key(name="ENTER")
    print(f"> Enter key by name: {enter_key}")

    a_key = find_key(pynput_key=keyboard.KeyCode.from_char("a"))
    print(f"> A key by pynput key: {a_key}")

    # Looking up mouse buttons
    right_button = find_button(name="RIGHT")
    print(f"> Right mouse button by name: {right_button}")

    middle_button = find_button(pynput_button=mouse.Button.middle)
    print(f"> Middle mouse button by pynput button: {middle_button}")
