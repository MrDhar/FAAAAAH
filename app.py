import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    from pynput import keyboard
except ImportError:
    keyboard = None

try:
    import pygame
except ImportError:
    pygame = None

APP_NAME = "Faaaaaah"
ACCENT = "#F4D83D"
GREEN = "#7FE0A7"
ORANGE = "#E5A95A"

if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).resolve().parent
else:
    BUNDLE_DIR = Path(__file__).resolve().parent
    APP_DIR = BUNDLE_DIR

ASSETS_DIR = BUNDLE_DIR / "assets"
PRESET_SOUND = ASSETS_DIR / "faaa.mp3"
MASCOT_IMAGE = ASSETS_DIR / "mascot_small.png"
if sys.platform.startswith("win"):
    _data_root = Path(os.environ.get("APPDATA", Path.home()))
elif sys.platform == "darwin":
    _data_root = Path.home() / "Library" / "Application Support"
else:
    _data_root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
USER_DIR = _data_root / "Faaaaaah"
SOUNDS_DIR = USER_DIR / "sounds"
CONFIG_FILE = USER_DIR / "settings.json"

# Shared light-theme palette (previously local to build_ui, which caused NameErrors elsewhere)
BG2 = "#EEF1F5"
GLASS = "#F8FAFC"
TEXT2 = "#17181A"
MUTED2 = "#737983"
PRESET_KEY = "preset"
PRESET_NAME = "Faaaaaah"


def ensure_user_dirs():
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    USER_DIR.mkdir(parents=True, exist_ok=True)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)

        ensure_user_dirs()

        self.enabled = True
        self.master_volume = 0.80
        self.sound_path = str(PRESET_SOUND)
        self.sound = None
        self.listener = None
        self._down = set()
        self.current_name_var = tk.StringVar(value=PRESET_NAME)

        self.load_settings()
        self.build_ui()
        self.init_audio()
        self.refresh_custom_sounds()
        self.start_listener()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    # ---------- persistence ----------
    def load_settings(self):
        try:
            if CONFIG_FILE.exists():
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                path = data.get("sound_path")
                if path == PRESET_KEY:
                    self.sound_path = str(PRESET_SOUND)
                elif path and Path(path).is_file():
                    self.sound_path = path
                self.master_volume = max(0.0, min(1.0, float(data.get("volume", 0.8))))
                self.enabled = bool(data.get("enabled", True))
        except Exception:
            pass

    @staticmethod
    def is_preset(path):
        try:
            return Path(path).resolve() == PRESET_SOUND.resolve()
        except Exception:
            return str(path) == str(PRESET_SOUND)

    def save_settings(self):
        try:
            ensure_user_dirs()
            CONFIG_FILE.write_text(
                json.dumps(
                    {
                        "sound_path": PRESET_KEY if self.is_preset(self.sound_path) else self.sound_path,
                        "volume": self.master_volume,
                        "enabled": self.enabled,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ---------- audio ----------
    def init_audio(self):
        if pygame is None:
            self.set_status("Audio library missing", False)
            return
        try:
            pygame.mixer.pre_init(44100, -16, 2, 256)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
            self.load_sound(self.sound_path, save=False)
        except Exception:
            self.set_status("Could not start audio", False)

    def load_sound(self, path, save=True):
        if pygame is None:
            return False
        try:
            new_sound = pygame.mixer.Sound(path)
            new_sound.set_volume(self.master_volume)
            self.sound = new_sound
            self.sound_path = str(path)
            self.current_name_var.set(PRESET_NAME if self.is_preset(path) else Path(path).stem)
            self.update_selected_visual()
            self.set_status("Ready", self.enabled)
            if save:
                self.save_settings()
            return True
        except Exception as exc:
            self.set_status("That sound could not be loaded", False)
            if save:
                messagebox.showerror(APP_NAME, f"Could not load this sound.\n\n{exc}")
            return False

    def play(self):
        if not self.enabled or self.sound is None or pygame is None:
            return
        try:
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(self.sound)
        except Exception:
            pass

    # ---------- keyboard ----------
    def on_release(self, key):
        self._down.discard(key)

    def on_press(self, key):
        if key in self._down:  # OS auto-repeat while a key is held
            return
        self._down.add(key)
        try:
            modifiers = {
                keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
                keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
                keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
            }
            if key in modifiers:
                return
        except Exception:
            pass
        self.play()

    def start_listener(self):
        if keyboard is None:
            self.set_status("Keyboard listener missing", False)
            return
        try:
            self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.daemon = True
            self.listener.start()
        except Exception:
            self.set_status("Could not listen for keys", False)

    # ---------- UI ----------
    def font(self, size, weight="normal"):
        # Apple-inspired typography with graceful Windows fallbacks.
        families = ("SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI")
        try:
            available = set(tkfont.families(self.root))
            family = next((name for name in families if name in available), "Segoe UI")
        except Exception:
            family = "Segoe UI"
        return (family, size, weight)

    def rounded_button(self, parent, text, command, width=None, primary=False, subtle=False):
        bg = ACCENT if primary else ("#EEF0F3" if not subtle else "#E8EAED")
        fg = "#17181A" if primary else "#25272A"
        active = "#FFE96A" if primary else "#DDE0E5"
        return self.flat_button(parent, text, command, bg, fg, active, self.font(10, "bold"), width, 14, 8)

    def flat_button(self, parent, text, command, bg, fg, active, font, width=None, padx=6, pady=3):
        # tk.Button ignores bg/fg on macOS; a bound Label looks the same everywhere.
        button = tk.Label(parent, text=text, font=font, bg=bg, fg=fg, cursor="hand2", padx=padx, pady=pady)
        if width:
            button.config(width=width)
        button.bind("<Button-1>", lambda _e: command())
        button.bind("<Enter>", lambda _e: button.config(bg=active))
        button.bind("<Leave>", lambda _e: button.config(bg=bg))
        return button

    def card(self, parent, bg="#F8FAFC", **kwargs):
        # Hairline border + pale surface gives a restrained frosted-glass impression.
        return tk.Frame(parent, bg=bg, highlightbackground="#DCE2E9", highlightthickness=1, bd=0, **kwargs)

    def build_ui(self):
        # Frosted-glass / iOS-inspired desktop surface. Tkinter cannot create a
        # true system blur layer, so the effect is deliberately subtle: layered
        # translucent-looking surfaces, hairline borders, soft depth and generous
        # spacing rather than heavy gradients or glossy effects.
        self.root.configure(bg=BG2)
        self.root.geometry("860x730")
        self.root.minsize(800, 660)

        # soft background layers create a quiet frosted-window feel
        backdrop = tk.Frame(self.root, bg=BG2)
        backdrop.pack(fill="both", expand=True)

        header = tk.Frame(backdrop, bg=BG2)
        header.pack(fill="x", padx=46, pady=(34, 18))
        try:
            self.mascot_image = tk.PhotoImage(file=str(MASCOT_IMAGE))
            factor = max(1, self.mascot_image.width() // 56)
            self.mascot_image = self.mascot_image.subsample(factor, factor)
            tk.Label(header, image=self.mascot_image, bg=BG2, bd=0).pack(side="left", padx=(0, 16))
        except Exception:
            self.mascot_image = None
        left = tk.Frame(header, bg=BG2)
        left.pack(side="left")
        tk.Label(left, text=APP_NAME, font=self.font(30, "bold"), fg=TEXT2, bg=BG2).pack(anchor="w")
        tk.Label(left, text="A tiny sound for every key you press.", font=self.font(10), fg=MUTED2, bg=BG2).pack(anchor="w", pady=(3, 0))

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Frame(header, bg=BG2)
        status.pack(side="right", pady=7)
        self.status_dot = tk.Label(status, text="●", font=self.font(8), fg="#34C759", bg=BG2)
        self.status_dot.pack(side="left", padx=(0, 6))
        tk.Label(status, textvariable=self.status_var, font=self.font(10, "bold"), fg=MUTED2, bg=BG2).pack(side="left")

        # Main glass hero
        hero = self.card(backdrop, bg=GLASS)
        hero.pack(fill="x", padx=46)
        hero_left = tk.Frame(hero, bg=GLASS)
        hero_left.pack(side="left", fill="both", expand=True, padx=28, pady=26)
        tk.Label(hero_left, text="CURRENT SOUND", font=self.font(9, "bold"), fg=MUTED2, bg=GLASS).pack(anchor="w")
        tk.Label(hero_left, text="FAAAAAH!", font=self.font(36, "bold"), fg=ACCENT, bg=GLASS).pack(anchor="w", pady=(3, 0))
        tk.Label(hero_left, textvariable=self.current_name_var, font=self.font(10), fg=TEXT2, bg=GLASS).pack(anchor="w", pady=(2, 0))

        hero_right = tk.Frame(hero, bg=GLASS)
        hero_right.pack(side="right", padx=28, pady=24)
        self.toggle_canvas = tk.Canvas(hero_right, width=72, height=42, bg=GLASS, highlightthickness=0, cursor="hand2")
        self.toggle_canvas.pack()
        self.toggle_canvas.bind("<Button-1>", lambda _e: self.toggle())
        self.draw_toggle()
        self.toggle_label = tk.Label(hero_right, text="Sound On" if self.enabled else "Sound Off", font=self.font(9, "bold"), fg=MUTED2, bg=GLASS)
        self.toggle_label.pack(pady=(6, 0))

        controls = tk.Frame(backdrop, bg=BG2)
        controls.pack(fill="x", padx=46, pady=16)

        volume = self.card(controls, bg=GLASS)
        volume.pack(side="left", fill="both", expand=True, padx=(0, 8))
        vtop = tk.Frame(volume, bg=GLASS)
        vtop.pack(fill="x", padx=20, pady=(15, 4))
        tk.Label(vtop, text="Volume", font=self.font(10, "bold"), fg=TEXT2, bg=GLASS).pack(side="left")
        self.vol_label = tk.Label(vtop, text=f"{int(self.master_volume * 100)}%", font=self.font(10), fg=MUTED2, bg=GLASS)
        self.vol_label.pack(side="right")
        self.volume_var = tk.DoubleVar(value=self.master_volume * 100)
        self.volume_scale = tk.Scale(volume, from_=0, to=100, orient="horizontal", variable=self.volume_var,
            command=self.change_volume, showvalue=False, highlightthickness=0, bg=GLASS, fg=TEXT2,
            troughcolor="#D9DEE5", activebackground=ACCENT, sliderrelief="flat", bd=0, length=280)
        self.volume_scale.pack(fill="x", padx=14, pady=(0, 10))
        self.volume_scale.bind("<ButtonRelease-1>", lambda _e: self.save_settings())

        test = self.card(controls, bg=GLASS)
        test.pack(side="right", fill="both", expand=True, padx=(8, 0))
        tk.Label(test, text="Test sound", font=self.font(10, "bold"), fg=TEXT2, bg=GLASS).pack(side="left", padx=20, pady=16)
        self.rounded_button(test, "Play Faaaaaah", self.play, primary=True).pack(side="right", padx=14, pady=10)

        library = self.card(backdrop, bg=GLASS)
        library.pack(fill="both", expand=True, padx=46, pady=(0, 16))
        top = tk.Frame(library, bg=GLASS)
        top.pack(fill="x", padx=22, pady=(20, 4))
        tk.Label(top, text="Sounds", font=self.font(18, "bold"), fg=TEXT2, bg=GLASS).pack(side="left")
        self.rounded_button(top, "+ Add Sound", self.add_sound, primary=True).pack(side="right")
        tk.Label(library, text="Faaaaaah is included. Add your own MP3 or WAV when you want.", font=self.font(9), fg=MUTED2, bg=GLASS).pack(anchor="w", padx=22)

        self.sound_list = tk.Frame(library, bg=GLASS)
        self.sound_list.pack(fill="both", expand=True, padx=18, pady=12)

        footer = tk.Frame(backdrop, bg=BG2)
        footer.pack(fill="x", padx=46, pady=(0, 20))
        tk.Label(footer, text="Modifier keys are silent", font=self.font(9), fg=MUTED2, bg=BG2).pack(side="left")
        self.flat_button(footer, "Open sound folder", self.open_sound_folder, BG2, MUTED2, BG2,
                         self.font(9, "bold"), padx=0, pady=0).pack(side="right")

    def draw_toggle(self):
        self.toggle_canvas.delete("all")
        on = self.enabled
        track = ACCENT if on else "#D8DDE4"
        self.toggle_canvas.create_oval(2, 2, 40, 40, fill=track, outline=track)
        self.toggle_canvas.create_oval(32, 2, 70, 40, fill=track, outline=track)
        self.toggle_canvas.create_rectangle(21, 2, 51, 40, fill=track, outline=track)
        x = 51 if on else 21
        self.toggle_canvas.create_oval(x - 14, 7, x + 14, 35, fill="#FFFFFF", outline="#D4D8DE")

    def update_selected_visual(self):
        self.refresh_custom_sounds()

    def refresh_custom_sounds(self):
        for child in self.sound_list.winfo_children():
            child.destroy()

        self.sound_card(self.sound_list, PRESET_NAME, PRESET_SOUND, True, self.is_preset(self.sound_path))

        files = []
        try:
            files = sorted([p for p in SOUNDS_DIR.iterdir() if p.suffix.lower() in (".mp3", ".wav")], key=lambda p: p.name.lower())
        except Exception:
            pass
        if not files:
            tk.Label(self.sound_list, text="No custom sounds yet", font=self.font(9), fg=MUTED2, bg=GLASS).pack(anchor="w", padx=12, pady=(6, 2))
        else:
            current = Path(self.sound_path).resolve()
            for p in files:
                self.sound_card(self.sound_list, p.stem, p, False, current == p.resolve())

    def sound_card(self, parent, name, path, preset, selected):
        CARD = "#F8F8FA"
        BORDER2 = "#E5E6E9"
        border = ACCENT if selected else BORDER2
        row = tk.Frame(parent, bg=CARD, highlightbackground=border, highlightthickness=1, cursor="hand2")
        row.pack(fill="x", pady=4)
        dot = tk.Canvas(row, width=34, height=34, bg=CARD, highlightthickness=0)
        dot.pack(side="left", padx=(12, 8), pady=8)
        dot.create_oval(3, 3, 31, 31, fill=ACCENT if preset else "#E1E3E7", outline="")
        dot.create_text(17, 17, text="♪" if preset else "•", fill="#17181A", font=self.font(12, "bold"))
        info = tk.Frame(row, bg=CARD)
        info.pack(side="left", fill="x", expand=True, pady=9)
        tk.Label(info, text=name, font=self.font(10, "bold"), fg=TEXT2, bg=CARD).pack(anchor="w")
        tk.Label(info, text="Preset" if preset else "Custom", font=self.font(8), fg=MUTED2, bg=CARD).pack(anchor="w", pady=(1, 0))
        if selected:
            tk.Label(row, text="Selected", font=self.font(8, "bold"), fg="#8A6D00", bg=CARD).pack(side="right", padx=10)
        self.rounded_button(row, "▶", lambda p=str(path): self.preview_path(p), width=3, subtle=True).pack(side="right", padx=(4, 8), pady=7)
        if not preset:
            self.flat_button(row, "Delete", lambda p=path: self.delete_custom(p), CARD, "#B42318", CARD,
                             self.font(8, "bold"), padx=5, pady=0).pack(side="right", padx=5)

        def select(_event=None, p=str(path)):
            self.load_sound(p)  # saves settings and refreshes the list itself
        for widget in (row, dot, info, *info.winfo_children()):
            widget.bind("<Button-1>", select)

    # ---------- actions ----------
    def preview_path(self, path):
        if pygame is None:
            return
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.master_volume)
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(sound)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not play this sound.\n\n{exc}")

    def add_sound(self):
        path = filedialog.askopenfilename(
            title="Add a custom sound",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("MP3 audio", "*.mp3"), ("WAV audio", "*.wav")],
        )
        if not path:
            return
        source = Path(path)
        target = SOUNDS_DIR / source.name
        if target.exists():
            i = 2
            while target.exists():
                target = SOUNDS_DIR / f"{source.stem} ({i}){source.suffix}"
                i += 1
        try:
            SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if not self.load_sound(str(target)):
                target.unlink(missing_ok=True)  # don't keep files that can't be decoded
            self.refresh_custom_sounds()
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not add this sound.\n\n{exc}")

    def delete_custom(self, path):
        if messagebox.askyesno(APP_NAME, f"Remove '{Path(path).stem}' from your custom sounds?"):
            try:
                was_selected = Path(path).resolve() == Path(self.sound_path).resolve()
                Path(path).unlink(missing_ok=True)
                if was_selected:
                    self.load_sound(str(PRESET_SOUND))
                self.refresh_custom_sounds()
            except Exception as exc:
                messagebox.showerror(APP_NAME, f"Could not remove this sound.\n\n{exc}")

    def open_sound_folder(self):
        ensure_user_dirs()
        try:
            if sys.platform.startswith("win"):
                os.startfile(SOUNDS_DIR)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(SOUNDS_DIR)])
            else:
                subprocess.Popen(["xdg-open", str(SOUNDS_DIR)])
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def change_volume(self, value):
        self.master_volume = max(0.0, min(1.0, float(value) / 100))
        self.vol_label.config(text=f"{int(float(value))}%")
        if self.sound:
            self.sound.set_volume(self.master_volume)

    def toggle(self):
        self.enabled = not self.enabled
        self.draw_toggle()
        if hasattr(self, "toggle_label"):
            self.toggle_label.config(text="Sound On" if self.enabled else "Sound Off")
        self.set_status("Ready" if self.enabled else "Paused", self.enabled)
        self.save_settings()

    def set_status(self, text, active=True):
        self.status_var.set(text)
        self.status_dot.config(fg=GREEN if active else ORANGE)

    def close(self):
        try:
            if self.listener:
                self.listener.stop()
            self.save_settings()
            if pygame:
                pygame.mixer.quit()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
