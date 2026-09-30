import os
import sys
from pathlib import Path

APP_NAME = "Faaaaaah"
WINDOW_TITLE = "Faaaaaah  -  every key has a voice"
PRESET_NAME = "Faaaaaah"
PRESET_KEY = "preset"

ACCENT = "#F4D83D"
ACCENT_HOVER = "#FFE566"
ACCENT_DEEP = "#E9B800"
GOLD_TEXT = "#D9A400"
INK = "#1D1D1F"
MUTED = "#86868B"
BG = "#F5F6FA"
SIDEBAR = "#E8EBF3"
NAV_HOVER = "#D7DBE5"
CARD = "#FFFFFF"
BORDER = "#E3E6EE"
SHADOW = "#E6E9F0"
SOFT = "#EEF0F5"
SOFT_HOVER = "#D7DBE5"
SELECTED_ROW = "#FFFBE3"
GREEN = "#34C759"
ORANGE = "#FF9F0A"
RED = "#D92D20"

if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    BUNDLE_DIR = Path(__file__).resolve().parents[2]

ASSETS_DIR = BUNDLE_DIR / "assets"
PRESET_SOUND = ASSETS_DIR / "faaa.mp3"
AVATAR_IMAGE = ASSETS_DIR / "avatar_56.png"
HERO_IMAGE = ASSETS_DIR / "hero_128.png"
ICON_PNG = ASSETS_DIR / "icon_256.png"
ICON_ICO = ASSETS_DIR / "Faaaaaah.ico"

if sys.platform.startswith("win"):
    DATA_ROOT = Path(os.environ.get("APPDATA", Path.home()))
elif sys.platform == "darwin":
    DATA_ROOT = Path.home() / "Library" / "Application Support"
else:
    DATA_ROOT = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

USER_DIR = DATA_ROOT / APP_NAME
SOUNDS_DIR = USER_DIR / "sounds"
CONFIG_FILE = USER_DIR / "settings.json"

MODIFIER_IDS = {"shift", "ctrl", "alt", "cmd", "alt_gr"}
PRETTY_KEYS = {
    "space": "Space", "enter": "Return", "backspace": "Delete", "tab": "Tab", "esc": "Esc",
    "shift": "Shift", "ctrl": "Control", "alt": "Alt", "alt_gr": "Alt Gr",
    "cmd": "Win" if sys.platform.startswith("win") else "Cmd",
    "caps_lock": "Caps Lock", "delete": "Del", "up": "Up", "down": "Down", "left": "Left",
    "right": "Right", "home": "Home", "end": "End", "page_up": "PgUp", "page_down": "PgDn",
    "insert": "Ins", "menu": "Menu", "num_lock": "Num Lock", "print_screen": "PrtSc",
}

def ensure_user_dirs():
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    USER_DIR.mkdir(parents=True, exist_ok=True)
