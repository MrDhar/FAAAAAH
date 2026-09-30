import sys
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
from pathlib import Path

from faaaaaah.core.config import (
    ACCENT, APP_NAME, AVATAR_IMAGE, BG, BORDER, CARD, GOLD_TEXT, GREEN,
    HERO_IMAGE, ICON_ICO, ICON_PNG, INK, MODIFIER_IDS, MUTED,
    ORANGE, PRESET_NAME, PRESET_SOUND, RED, SELECTED_ROW, SIDEBAR, SOFT,
    SOFT_HOVER, WINDOW_TITLE, ensure_user_dirs,
)
from faaaaaah.core.keys import pretty_key, same_path
from faaaaaah.core.settings import SettingsStore
from faaaaaah.core.audio import AudioEngine
from faaaaaah.core.sounds import SoundLibrary
from faaaaaah.core.keyboard import KeyboardService
from faaaaaah.ui.widgets import Card, Pill, Toggle, VolumeSlider, ScrollFrame, NavItem, make_keycap
from faaaaaah.ui.dialogs import AssignDialog

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        ensure_user_dirs()

        self.enabled = True
        self.master_volume = 0.80
        self.sound_path = str(PRESET_SOUND)
        self.key_map = {}
        self.key_sound_enabled = {}
        self.recent_activity = []
        self.last_key_var = tk.StringVar(value="No key pressed yet")
        self.last_sound_var = tk.StringVar(value=PRESET_NAME)
        self.icon_img = self.avatar_img = self.hero_img = None
        self.current_name_var = tk.StringVar(value=PRESET_NAME)

        self.settings = SettingsStore()
        self.audio = AudioEngine(on_error=lambda msg: self.set_status(msg, False) if hasattr(self, "status_var") else None)
        self.sound_library = SoundLibrary(self.audio, lambda msg: messagebox.showerror(APP_NAME, msg))
        self.keyboard_service = KeyboardService(self.handle_key, lambda msg: self.set_status(msg, False) if hasattr(self, "status_var") else None)

        try:
            available = set(tkfont.families(root))
            self.family = next((n for n in ("SF Pro Display", "SF Pro Text", "Helvetica Neue",
                                            "Segoe UI Variable Display", "Segoe UI") if n in available), "Segoe UI")
        except Exception:
            self.family = "Segoe UI"

        self.load_settings()
        self.audio.set_volume(self.master_volume)
        # AudioEngine stays enabled; the app-level toggle controls only fallback/global sounds.
        # Key-specific sounds have their own independent toggles.
        self.audio.enabled = True
        self.build_ui()
        self.init_audio()
        self.refresh_sounds()
        self.refresh_keys()
        self.keyboard_service.start()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def load_settings(self):
        data = self.settings.load()
        self.sound_path = data["sound_path"]
        self.master_volume = data["volume"]
        self.enabled = data["enabled"]
        self.key_map = dict(data["key_sounds"])
        self.key_sound_enabled = {k: bool(v) for k, v in data.get("key_sound_enabled", {}).items() if k in self.key_map}
        for kid in self.key_map:
            self.key_sound_enabled.setdefault(kid, True)

    def save_settings(self):
        self.settings.save(self.sound_path, self.master_volume, self.enabled, self.key_map, self.key_sound_enabled)

    def init_audio(self):
        if self.audio.start():
            if self.audio.load(self.sound_path):
                self.current_name_var.set(self.sound_library.name(self.sound_path))
                self.set_status("Ready", self.enabled)
            else:
                self.set_status("That sound could not be loaded", False)

    def load_sound(self, path, save=True):
        if not self.audio.available:
            self.set_status("Audio library missing", False)
            return False
        if self.audio.load(path):
            self.sound_path = str(path)
            self.current_name_var.set(self.sound_library.name(path))
            self.refresh_sounds()
            self.set_status("Ready", self.enabled)
            if save:
                self.save_settings()
            return True
        self.set_status("That sound could not be loaded", False)
        if save:
            messagebox.showerror(APP_NAME, "Could not load this sound.")
        return False

    def available_sounds(self):
        return self.sound_library.available()

    def sound_name(self, path):
        return self.sound_library.name(path)

    def handle_key(self, kid):
        # pynput calls this on a worker thread; Tk widgets must only be touched
        # from Tk's main thread.
        try:
            self.root.after(0, lambda k=kid: self._handle_key_ui(k))
        except tk.TclError:
            pass

    def _handle_key_ui(self, kid):
        if kid in MODIFIER_IDS:
            return

        mapped = kid in self.key_map
        if mapped:
            if not self.key_sound_enabled.get(kid, True):
                return
            path = self.key_map[kid]
            source = "custom"
        else:
            if not self.enabled:
                return
            path = self.sound_path
            source = "default"

        self.audio.play_path(path)
        pretty = pretty_key(kid)
        sound_name = self.sound_name(path)
        self.last_key_var.set(f"Pressed {pretty}")
        self.last_sound_var.set(sound_name)
        self.recent_activity.insert(0, (pretty, sound_name, source))
        del self.recent_activity[6:]
        self.refresh_activity()

    def font(self, size, weight="normal"):
        return (self.family, size, weight)

    def load_images(self):
        for attr, path in (("avatar_img", AVATAR_IMAGE), ("hero_img", HERO_IMAGE), ("icon_img", ICON_PNG)):
            try:
                setattr(self, attr, tk.PhotoImage(file=str(path)))
            except Exception:
                setattr(self, attr, None)

    def set_window_icon(self):
        done = False
        if sys.platform.startswith("win") and ICON_ICO.exists():
            try:
                self.root.iconbitmap(default=str(ICON_ICO))
                done = True
            except Exception:
                pass
        if not done and self.icon_img is not None:
            try:
                self.root.iconphoto(True, self.icon_img)
            except Exception:
                pass

    def page_header(self, parent, title, subtitle, action=None):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", padx=34, pady=(30, 18))
        left = tk.Frame(row, bg=BG)
        left.pack(side="left")
        tk.Label(left, text=title, font=self.font(26, "bold"), fg=INK, bg=BG).pack(anchor="w")
        tk.Label(left, text=subtitle, font=self.font(10), fg=MUTED, bg=BG).pack(anchor="w", pady=(2, 0))
        if action:
            Pill(row, action[0], action[1], self.font(10, "bold"), outer=BG, padx=20, pady=9).pack(side="right", anchor="center")

    # ---------- UI ----------
    def build_ui(self):
        root = self.root
        root.configure(bg=BG)
        w, h = 980, 700
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        w, h = min(w, sw - 40), min(h, sh - 80)
        root.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 3)}")
        root.minsize(860, 580)
        self.load_images()
        self.set_window_icon()

        shell = tk.Frame(root, bg=BG)
        shell.pack(fill="both", expand=True)
        self.sidebar = tk.Frame(shell, bg=SIDEBAR, width=238)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Frame(shell, bg=BORDER, width=1).pack(side="left", fill="y")
        self.content = tk.Frame(shell, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.build_sidebar()

        self.pages = {}
        for name, builder in (("home", self.build_home), ("sounds", self.build_sounds), ("keys", self.build_keys)):
            sf = ScrollFrame(self.content, BG)
            builder(sf.inner)
            self.pages[name] = sf
        self.current = None
        self.show_page("home")

        root.bind_all("<MouseWheel>", self._on_wheel)
        root.bind_all("<Button-4>", lambda e: self._scroll_for(e, -1))
        root.bind_all("<Button-5>", lambda e: self._scroll_for(e, 1))

    def _scroll_for(self, event, units):
        try:
            top = event.widget.winfo_toplevel()
        except Exception:
            return
        target = self.pages.get(self.current) if top is self.root else getattr(top, "scroller", None)
        if target:
            target.scroll(units)

    def _on_wheel(self, event):
        self._scroll_for(event, -1 if event.delta > 0 else 1)

    def build_sidebar(self):
        sb = self.sidebar
        brand = tk.Frame(sb, bg=SIDEBAR)
        brand.pack(fill="x", padx=20, pady=(28, 26))
        if self.avatar_img:
            tk.Label(brand, image=self.avatar_img, bg=SIDEBAR, bd=0).pack(side="left", padx=(0, 12))
        names = tk.Frame(brand, bg=SIDEBAR)
        names.pack(side="left")
        tk.Label(names, text=APP_NAME, font=self.font(17, "bold"), fg=INK, bg=SIDEBAR).pack(anchor="w")
        tk.Label(names, text="Every key, a voice", font=self.font(9), fg=MUTED, bg=SIDEBAR).pack(anchor="w")

        self.nav = {}
        for key, text, kind, color in (("home", "Now Playing", "home", ORANGE),
                                       ("sounds", "Sounds", "sounds", "#AF52DE"),
                                       ("keys", "Key Sounds", "keys", "#0A84FF")):
            item = NavItem(sb, text, kind, color, lambda k=key: self.show_page(k), self.font(11, "bold"))
            item.pack(padx=17, pady=2, anchor="w")
            self.nav[key] = item

        creator = tk.Frame(sb, bg=SIDEBAR)
        creator.pack(side="bottom", fill="x", padx=24, pady=(0, 8))
        tk.Label(creator, text="Created by Anurodh Dhar", font=self.font(8), fg=MUTED, bg=SIDEBAR).pack(anchor="w")

        status = tk.Frame(sb, bg=SIDEBAR)
        status.pack(side="bottom", fill="x", padx=24, pady=(0, 12))
        self.status_var = tk.StringVar(value="Ready")
        self.status_dot = tk.Label(status, text="\u25cf", font=self.font(9), fg=GREEN, bg=SIDEBAR)
        self.status_dot.pack(side="left", padx=(0, 7))
        tk.Label(status, textvariable=self.status_var, font=self.font(10, "bold"), fg=MUTED, bg=SIDEBAR).pack(side="left")

    def show_page(self, name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[name].pack(fill="both", expand=True)
        self.pages[name].canvas.yview_moveto(0)
        self.current = name
        for k, item in self.nav.items():
            item._set(selected=(k == name))

    # ----- Home -----
    def build_home(self, p):
        self.page_header(p, "Now Playing", "Control your default sound, volume, and see what Faaaaaah played most recently.")

        hero = Card(p, radius=22)
        hero.pack(fill="x", padx=34)
        hi = hero.inner
        if self.hero_img:
            tk.Label(hi, image=self.hero_img, bg=CARD, bd=0).pack(side="left", padx=(14, 18), pady=14)
        txt = tk.Frame(hi, bg=CARD)
        txt.pack(side="left", anchor="center", fill="x", expand=True)
        tk.Label(txt, text="ACTIVE SOUND", font=self.font(9, "bold"), fg=MUTED, bg=CARD).pack(anchor="w")
        tk.Label(txt, textvariable=self.current_name_var, font=self.font(25, "bold"), fg=GOLD_TEXT, bg=CARD).pack(anchor="w")
        tk.Label(txt, textvariable=self.last_sound_var, font=self.font(10), fg=MUTED, bg=CARD).pack(anchor="w", pady=(1, 0))
        right = tk.Frame(hi, bg=CARD)
        right.pack(side="right", anchor="center", padx=(16, 18))
        self.toggle_switch = Toggle(right, self.enabled, self.toggle, CARD)
        self.toggle_switch.pack()
        self.toggle_label = tk.Label(right, text="Sound On" if self.enabled else "Sound Off",
                                     font=self.font(9, "bold"), fg=MUTED, bg=CARD)
        self.toggle_label.pack(pady=(6, 0))

        row = tk.Frame(p, bg=BG)
        row.pack(fill="x", padx=34, pady=18)
        row.columnconfigure((0, 1), weight=1, uniform="cols")

        latest = Card(row)
        latest.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        tk.Label(latest.inner, text="Last key", font=self.font(11, "bold"), fg=INK, bg=CARD).pack(anchor="w", padx=14, pady=(12, 1))
        tk.Label(latest.inner, textvariable=self.last_key_var, font=self.font(13, "bold"), fg=INK, bg=CARD).pack(anchor="w", padx=14)
        tk.Label(latest.inner, text="Mapped keys use their own sound. Every other key uses your active sound.",
                 font=self.font(9), fg=MUTED, bg=CARD, wraplength=300, justify="left").pack(anchor="w", padx=14, pady=(3, 12))

        vol = Card(row)
        vol.grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        vtop = tk.Frame(vol.inner, bg=CARD)
        vtop.pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(vtop, text="Volume", font=self.font(11, "bold"), fg=INK, bg=CARD).pack(side="left")
        self.vol_label = tk.Label(vtop, text=f"{int(self.master_volume * 100)}%", font=self.font(11, "bold"),
                                  fg=GOLD_TEXT, bg=CARD)
        self.vol_label.pack(side="right")
        self.volume_slider = VolumeSlider(vol.inner, self.master_volume, self.change_volume, self.save_settings, CARD)
        self.volume_slider.pack(fill="x", padx=4, pady=(2, 8))

        activity = Card(p)
        activity.pack(fill="x", padx=34, pady=(0, 18))
        top = tk.Frame(activity.inner, bg=CARD)
        top.pack(fill="x", padx=14, pady=(12, 5))
        tk.Label(top, text="Recent activity", font=self.font(11, "bold"), fg=INK, bg=CARD).pack(side="left")
        Pill(top, "Play active sound", self.test_sound, self.font(9, "bold"), outer=CARD, fill=SOFT, hover=SOFT_HOVER, padx=12, pady=5).pack(side="right")
        self.activity_list = tk.Frame(activity.inner, bg=CARD)
        self.activity_list.pack(fill="x", padx=14, pady=(0, 8))
        self.refresh_activity()

        # Cards created on this page need one explicit content measurement
        # after all dynamic widgets have been added. Without this they remain
        # at the Card's initial 10px height and appear as empty lines.
        for card in (hero, latest, vol, activity):
            card.resize_to_content()


    def refresh_activity(self):
        if not hasattr(self, "activity_list"):
            return
        for child in self.activity_list.winfo_children():
            child.destroy()
        if not self.recent_activity:
            tk.Label(self.activity_list, text="No key presses yet. Start typing and the latest sounds will appear here.",
                     font=self.font(9), fg=MUTED, bg=CARD).pack(anchor="w", pady=(4, 8))
            return
        for idx, (key, sound, source) in enumerate(self.recent_activity):
            if idx:
                tk.Frame(self.activity_list, bg=SOFT, height=1).pack(fill="x", padx=2)
            row = tk.Frame(self.activity_list, bg=CARD)
            row.pack(fill="x", pady=5)
            make_keycap(row, key, CARD, self.font(9, "bold"), 0.85).pack(side="left")
            tk.Label(row, text=sound, font=self.font(9, "bold"), fg=INK, bg=CARD).pack(side="left", padx=10)
            tk.Label(row, text="key sound" if source == "custom" else "default", font=self.font(8), fg=MUTED, bg=CARD).pack(side="right")

    # ----- Sounds -----
    def build_sounds(self, p):
        self.page_header(p, "Sounds", "Faaaaaah is included. Add your own MP3 or WAV.", ("+ Add Sound", self.add_sound))
        card = Card(p)
        card.pack(fill="x", padx=34, pady=(0, 30))
        self.sound_card = card
        self.sound_list = card.inner

    def refresh_sounds(self):
        if not hasattr(self, "sound_list"):
            return
        for c in self.sound_list.winfo_children():
            c.destroy()
        items = self.available_sounds()
        for i, (name, path, preset) in enumerate(items):
            if i:
                tk.Frame(self.sound_list, bg=SOFT, height=1).pack(fill="x", padx=14)
            self.sound_row(self.sound_list, name, path, preset, same_path(path, self.sound_path))
        if len(items) == 1:
            tk.Label(self.sound_list, text="No custom sounds yet - tap + Add Sound", font=self.font(9),
                     fg=MUTED, bg=CARD).pack(anchor="w", padx=18, pady=(8, 10))
        self.sound_card.resize_to_content()

    def sound_row(self, parent, name, path, preset, selected):
        f = self.font
        bg = SELECTED_ROW if selected else CARD
        row = tk.Frame(parent, bg=bg, cursor="hand2")
        row.pack(fill="x")
        dot = tk.Canvas(row, width=38, height=38, bg=bg, highlightthickness=0)
        dot.pack(side="left", padx=(14, 10), pady=10)
        dot.create_oval(3, 3, 35, 35, fill=ACCENT if preset else SOFT_HOVER, outline="")
        dot.create_text(19, 19, text="\u266a" if preset else "\u2022", fill=INK, font=f(13, "bold"))
        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="x", expand=True, pady=10)
        tk.Label(info, text=name, font=f(11, "bold"), fg=INK, bg=bg).pack(anchor="w")
        tk.Label(info, text="Preset" if preset else "Custom", font=f(9), fg=MUTED, bg=bg).pack(anchor="w")
        Pill(row, "\u25b6", lambda p=str(path): self.preview_path(p), f(9, "bold"), outer=bg, fill=SOFT,
             hover=SOFT_HOVER, padx=12, pady=5).pack(side="right", padx=(6, 14))
        if selected:
            Pill(row, "Selected", None, f(9, "bold"), outer=bg, padx=12, pady=4).pack(side="right", padx=4)
        if not preset:
            d = tk.Label(row, text="Delete", font=f(9, "bold"), fg=RED, bg=bg, cursor="hand2")
            d.pack(side="right", padx=8)
            d.bind("<Button-1>", lambda _e, p=path: self.delete_custom(p))
        for wdg in (row, dot, info, *info.winfo_children()):
            wdg.bind("<Button-1>", lambda _e, p=str(path): self.load_sound(p))

    # ----- Key Sounds -----
    def build_keys(self, p):
        self.page_header(
            p,
            "Key Sounds",
            "Give individual keys their own sound and control them independently.",
            ("+ Assign Key", self.open_assign),
        )

        tip = Card(p)
        tip.pack(fill="x", padx=34, pady=(0, 14))
        tip_inner = tip.inner

        tk.Label(
            tip_inner,
            text="How key sounds work",
            font=self.font(10, "bold"),
            fg=INK,
            bg=CARD,
        ).pack(anchor="w", padx=16, pady=(12, 2))

        tk.Label(
            tip_inner,
            text="Each assigned key has its own On/Off switch. The Default sound switch does not affect enabled key-specific sounds.",
            font=self.font(9),
            fg=MUTED,
            bg=CARD,
        ).pack(anchor="w", padx=16, pady=(0, 12))

        card = Card(p)
        card.pack(fill="x", padx=34, pady=(0, 30))
        self.keys_card = card
        self.keys_list = card.inner

    def refresh_keys(self):
        if not hasattr(self, "keys_list"):
            return
        for c in self.keys_list.winfo_children():
            c.destroy()
        f = self.font
        if not self.key_map:
            empty = tk.Frame(self.keys_list, bg=CARD)
            empty.pack(fill="x", pady=26)
            tk.Label(empty, text="No key-specific sounds yet", font=f(13, "bold"), fg=INK, bg=CARD).pack()
            tk.Label(empty, text="Use + Assign Key above to give one keyboard key its own sound.",
                     font=f(10), fg=MUTED, bg=CARD, wraplength=520, justify="center").pack(pady=(6, 4))
            self.keys_card.resize_to_content()
            return
        for i, (kid, path) in enumerate(sorted(self.key_map.items(), key=lambda kv: pretty_key(kv[0]).lower())):
            if i:
                tk.Frame(self.keys_list, bg=SOFT, height=1).pack(fill="x", padx=14)
            row = tk.Frame(self.keys_list, bg=CARD)
            row.pack(fill="x")
            make_keycap(row, pretty_key(kid), CARD, f(12, "bold")).pack(side="left", padx=(14, 14), pady=10)
            info = tk.Frame(row, bg=CARD)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=self.sound_name(path), font=f(11, "bold"), fg=INK, bg=CARD).pack(anchor="w")
            tk.Label(info, text="Plays when you press " + pretty_key(kid), font=f(9), fg=MUTED, bg=CARD).pack(anchor="w")
            toggle_wrap = tk.Frame(row, bg=CARD)
            toggle_wrap.pack(side="right", padx=(6, 10))
            key_toggle = Toggle(toggle_wrap, self.key_sound_enabled.get(kid, True),
                                lambda k=kid: self.toggle_key_sound(k), CARD)
            key_toggle.pack(side="left")
            tk.Label(toggle_wrap, text="On" if self.key_sound_enabled.get(kid, True) else "Off",
                     font=f(8, "bold"), fg=MUTED, bg=CARD).pack(side="left", padx=(5, 0))
            rm = tk.Label(row, text="Remove", font=f(9, "bold"), fg=RED, bg=CARD, cursor="hand2")
            rm.pack(side="right", padx=(8, 14))
            rm.bind("<Button-1>", lambda _e, k=kid: self.remove_key(k))
            Pill(row, "Change", lambda k=kid, p=path: self.open_assign(k, p), f(9, "bold"), fill=SOFT,
                 hover=SOFT_HOVER, padx=14, pady=5).pack(side="right", padx=4)
            Pill(row, "\u25b6", lambda p=path: self.preview_path(p), f(9, "bold"), fill=SOFT,
                 hover=SOFT_HOVER, padx=12, pady=5).pack(side="right", padx=4)
        self.keys_card.resize_to_content()

    # ---------- actions ----------
    def open_assign(self, key=None, sound=None):
        AssignDialog(self, key if isinstance(key, str) else None, sound)

    def assign_key(self, kid, path):
        self.key_map[kid] = str(path)
        self.key_sound_enabled.setdefault(kid, True)
        self.save_settings()
        self.refresh_keys()

    def toggle_key_sound(self, kid):
        if kid not in self.key_map:
            return
        self.key_sound_enabled[kid] = not self.key_sound_enabled.get(kid, True)
        self.save_settings()
        self.refresh_keys()

    def remove_key(self, kid):
        self.key_map.pop(kid, None)
        self.key_sound_enabled.pop(kid, None)
        self.save_settings()
        self.refresh_keys()

    def test_sound(self):
        self.preview_path(self.sound_path)

    def preview_path(self, path):
        if not self.audio.available:
            return
        sound = self.audio.get(path)
        if sound is None:
            messagebox.showerror(APP_NAME, "Could not play this sound.")
            return
        self.audio.play(sound)

    def import_sound(self, path):
        return self.sound_library.import_file(path)

    def add_sound(self):
        path = filedialog.askopenfilename(
            title="Add a custom sound",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("MP3 audio", "*.mp3"), ("WAV audio", "*.wav")],
        )
        if not path:
            return
        target = self.import_sound(path)
        if target:
            self.load_sound(str(target))

    def delete_custom(self, path):
        if messagebox.askyesno(APP_NAME, f"Remove '{Path(path).stem}' from your custom sounds?"):
            try:
                was_selected = same_path(path, self.sound_path)
                self.audio.cache.pop(str(path), None)
                Path(path).unlink(missing_ok=True)
                for kid in [k for k, v in self.key_map.items() if same_path(v, path)]:
                    del self.key_map[kid]
                    self.key_sound_enabled.pop(kid, None)
                if was_selected:
                    self.load_sound(str(PRESET_SOUND))
                else:
                    self.save_settings()
                    self.refresh_sounds()
                self.refresh_keys()
            except Exception as exc:
                messagebox.showerror(APP_NAME, f"Could not remove this sound.\n\n{exc}")

    def change_volume(self, value):
        self.master_volume = max(0.0, min(1.0, float(value)))
        pct = int(round(self.master_volume * 100))
        if self.vol_label.cget("text") != f"{pct}%":
            self.vol_label.config(text=f"{pct}%")
        self.audio.set_volume(self.master_volume)

    def toggle(self):
        self.enabled = not self.enabled
        self.toggle_switch.set(self.enabled)
        self.toggle_label.config(text="Default sound On" if self.enabled else "Default sound Off")
        self.set_status("Ready" if self.enabled else "Paused", self.enabled)
        self.save_settings()

    def set_status(self, text, active=True):
        self.status_var.set(text)
        self.status_dot.config(fg=GREEN if active else ORANGE)

    def close(self):
        try:
            self.keyboard_service.stop()
            self.save_settings()
            self.audio.stop()
        except Exception:
            pass
        self.root.destroy()

