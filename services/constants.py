"""
Reference:
    https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#enum-QMP-ui.QKeyCode
"""
# fmt: off
KEY_MAPPING = {
    # Letters
    "A": "a", "B": "b", "C": "c", "D": "d", "E": "e", "F": "f", "G": "g", "H": "h", "I": "i",
    "J": "j", "K": "k", "L": "l", "M": "m", "N": "n", "O": "o", "P": "p", "Q": "q", "R": "r",
    "S": "s", "T": "t", "U": "u", "V": "v", "W": "w", "X": "x", "Y": "y", "Z": "z",
    
    # Numbers
    "0": "0", "1": "1", "2": "2", "3": "3", "4": "4", 
    "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
    
    # Function keys
    "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4", "F5": "f5", 
    "F6": "f6", "F7": "f7", "F8": "f8", "F9": "f9", "F10": "f10",
    "F11": "f11", "F12": "f12", "F13": "f13", "F14": "f14", "F15": "f15",
    "F16": "f16", "F17": "f17", "F18": "f18", "F19": "f19", "F20": "f20",
    "F21": "f21", "F22": "f22", "F23": "f23", "F24": "f24",
    
    # Special keys
    "SHIFT": "shift", "RIGHT_SHIFT": "shift_r", 
    "ALT": "alt", "RIGHT_ALT": "alt_r",
    "CTRL": "ctrl", "RIGHT_CTRL": "ctrl_r",
    "MENU": "menu", "ESC": "esc", "ESCAPE": "esc",
    
    # Symbols and punctuation
    "MINUS": "minus", "DASH": "minus", "HYPHEN": "minus",
    "EQUALS": "equal", "EQUAL": "equal", 
    "BACKSPACE": "backspace", "TAB": "tab",
    "LEFT_BRACKET": "bracket_left", "RIGHT_BRACKET": "bracket_right",
    "ENTER": "ret", "RETURN": "ret",
    "SEMICOLON": "semicolon", "COLON": "semicolon",  # No direct colon key
    "APOSTROPHE": "apostrophe", "QUOTE": "apostrophe",
    "GRAVE": "grave_accent", "BACKTICK": "grave_accent",
    "BACKSLASH": "backslash", "COMMA": "comma",
    "PERIOD": "dot", "DOT": "dot", "FULLSTOP": "dot",
    "SLASH": "slash", "FORWARD_SLASH": "slash",
    "ASTERISK": "asterisk", "STAR": "asterisk",
    
    # Whitespace and layout
    "SPACE": "spc", "CAPS_LOCK": "caps_lock", "CAPSLOCK": "caps_lock",
    
    # Number pad
    "NUM_LOCK": "num_lock", "NUMLOCK": "num_lock",
    "NUM_DIVIDE": "kp_divide", "NUM_MULTIPLY": "kp_multiply",
    "NUM_SUBTRACT": "kp_subtract", "NUM_MINUS": "kp_subtract",
    "NUM_ADD": "kp_add", "NUM_PLUS": "kp_add",
    "NUM_ENTER": "kp_enter", "NUM_DECIMAL": "kp_decimal",
    "NUM_0": "kp_0", "NUM_1": "kp_1", "NUM_2": "kp_2", "NUM_3": "kp_3", 
    "NUM_4": "kp_4", "NUM_5": "kp_5", "NUM_6": "kp_6", 
    "NUM_7": "kp_7", "NUM_8": "kp_8", "NUM_9": "kp_9",
    
    # Navigation
    "SCROLL_LOCK": "scroll_lock", "SCROLLLOCK": "scroll_lock",
    "PRINT": "print", "PRINTSCREEN": "print", "SYSRQ": "sysrq",
    "HOME": "home", "PAGE_UP": "pgup", "PAGEUP": "pgup",
    "PAGE_DOWN": "pgdn", "PAGEDOWN": "pgdn",
    "END": "end", "LEFT": "left", "UP": "up", "DOWN": "down", "RIGHT": "right",
    "INSERT": "insert", "DELETE": "delete", "DEL": "delete",
    
    # Media keys
    "VOLUME_UP": "volumeup", "VOLUME_DOWN": "volumedown",
    "AUDIO_NEXT": "audionext", "AUDIO_PREV": "audioprev", 
    "AUDIO_STOP": "audiostop", "AUDIO_PLAY": "audioplay",
    "AUDIO_MUTE": "audiomute",
    
    # Other
    "LESS": "less", "STOP": "stop", "AGAIN": "again", "PROPS": "props",
    "UNDO": "undo", "FRONT": "front", "COPY": "copy", "OPEN": "open",
    "PASTE": "paste", "FIND": "find", "CUT": "cut", "HELP": "help",
    "POWER": "power", "SLEEP": "sleep", "WAKE": "wake",
    "MAIL": "mail", "CALCULATOR": "calculator", "COMPUTER": "computer",
    "HOME_PAGE": "ac_home", "BACK": "ac_back", "FORWARD": "ac_forward",
    "REFRESH": "ac_refresh", "BOOKMARKS": "ac_bookmarks"
}
# fmt: on

"""
Reference:
    https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#enum-QMP-ui.InputButton
"""
# Mouse button mappings
MOUSE_BUTTON_MAPPING = {
    "LEFT": "left",
    "RIGHT": "right",
    "MIDDLE": "middle"
}

# Scroll direction mappings
SCROLL_MAPPING = {
    "UP": "wheel-up",
    "DOWN": "wheel-down",
    "LEFT": "wheel-left",
    "RIGHT": "wheel-right"
}
