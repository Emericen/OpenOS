"""
Reference:
    https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#enum-QMP-ui.QKeyCode
"""
# fmt: off
VALID_QEMU_KEYS = {
    "unmapped", "pause", "ro", "kp_comma", "kp_equals", "power", "hiragana", "henkan", 
    "yen", "sleep", "wake", "audionext", "audioprev", "audiostop", "audioplay", "audiomute", 
    "volumeup", "volumedown", "mediaselect", "mail", "calculator", "computer", "ac_home", 
    "ac_back", "ac_forward", "ac_refresh", "ac_bookmarks", "muhenkan", "katakanahiragana", 
    "lang1", "lang2", "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22", 
    "f23", "f24", "shift", "shift_r", "alt", "alt_r", "ctrl", "ctrl_r", "menu", "esc", "1", 
    "2", "3", "4", "5", "6", "7", "8", "9", "0", "minus", "equal", "backspace", "tab", "q", 
    "w", "e", "r", "t", "y", "u", "i", "o", "p", "bracket_left", "bracket_right", "ret", 
    "a", "s", "d", "f", "g", "h", "j", "k", "l", "semicolon", "apostrophe", "grave_accent", 
    "backslash", "z", "x", "c", "v", "b", "n", "m", "comma", "dot", "slash", "asterisk", 
    "spc", "caps_lock", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", 
    "num_lock", "scroll_lock", "kp_divide", "kp_multiply", "kp_subtract", "kp_add", 
    "kp_enter", "kp_decimal", "sysrq", "kp_0", "kp_1", "kp_2", "kp_3", "kp_4", "kp_5", 
    "kp_6", "kp_7", "kp_8", "kp_9", "less", "f11", "f12", "print", "home", "pgup", "pgdn", 
    "end", "left", "up", "down", "right", "insert", "delete", "stop", "again", "props", 
    "undo", "front", "copy", "open", "paste", "find", "cut", "lf", "help", "meta_l", 
    "meta_r", "compose"
}
# fmt: on

"""
Reference:
    https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#enum-QMP-ui.InputButton
"""
VALID_QEMU_MOUSE_BUTTONS = {"left", "right", "middle"}
VALID_QEMU_MOUSE_SCROLL_BUTTONS = {
    "wheel-up",
    "wheel-down",
    "wheel-left",
    "wheel-right",
}
