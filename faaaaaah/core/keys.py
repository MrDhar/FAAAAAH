import re
import sys
from pathlib import Path

from .config import PRETTY_KEYS


_TK_KEYSYMS = {
    "Return": "enter", "BackSpace": "backspace", "Tab": "tab", "Escape": "esc",
    "Shift_L": "shift", "Shift_R": "shift", "Control_L": "ctrl", "Control_R": "ctrl",
    "Alt_L": "alt", "Alt_R": "alt", "ISO_Level3_Shift": "alt_gr",
    "Super_L": "cmd", "Super_R": "cmd", "Win_L": "cmd", "Win_R": "cmd",
    "Caps_Lock": "caps_lock", "Delete": "delete", "Home": "home", "End": "end",
    "Prior": "page_up", "Next": "page_down", "Insert": "insert",
    "Up": "up", "Down": "down", "Left": "left", "Right": "right",
    "Num_Lock": "num_lock", "Print": "print_screen", "Menu": "menu",
    "KP_Enter": "enter",
}


def key_id(key):
    ch = getattr(key, "char", None)
    if ch and ch.isprintable() and not ch.isspace():
        return ch.lower()
    name = getattr(key, "name", None)
    if name:
        return re.sub(r"_(l|r)$", "", name)
    vk = getattr(key, "vk", None)
    if vk is not None:
        if sys.platform.startswith("win") and (48 <= vk <= 57 or 65 <= vk <= 90):
            return chr(vk).lower()
        return f"vk{vk}"
    return str(key)


def tk_key_id(event):
    """Normalize a Tk KeyPress event to the same IDs used by pynput."""
    char = getattr(event, "char", "")
    if char and char.isprintable() and not char.isspace():
        return char.lower()
    keysym = getattr(event, "keysym", "")
    if keysym in _TK_KEYSYMS:
        return _TK_KEYSYMS[keysym]
    lower = keysym.lower()
    if re.fullmatch(r"f\d{1,2}", lower):
        return lower
    if lower.startswith("kp_"):
        return lower[3:]
    return lower or None


def pretty_key(kid):
    if kid in PRETTY_KEYS:
        return PRETTY_KEYS[kid]
    if len(kid) == 1:
        return kid.upper()
    if re.fullmatch(r"f\d{1,2}", kid):
        return kid.upper()
    if kid.startswith("vk"):
        return "Key " + kid[2:]
    return kid.replace("_", " ").title()


def same_path(a, b):
    try:
        return Path(a).resolve() == Path(b).resolve()
    except Exception:
        return str(a) == str(b)
