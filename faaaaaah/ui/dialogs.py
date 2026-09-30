import sys
import tkinter as tk

from faaaaaah.core.config import (
    ACCENT, ACCENT_DEEP, ACCENT_HOVER, BG, CARD, ICON_ICO, INK, MUTED,
    PRESET_SOUND, SELECTED_ROW, SOFT, SOFT_HOVER, BORDER
)
from faaaaaah.core.keys import pretty_key, same_path, tk_key_id
from faaaaaah.ui.widgets import Card, Pill, ScrollFrame, make_keycap


class AssignDialog(tk.Toplevel):
    """Small, explicit wizard for assigning one key to one sound."""

    def __init__(self, app, key=None, sound=None):
        super().__init__(app.root)
        self.app = app
        self.key = key
        self.sound = str(sound) if sound else str(PRESET_SOUND)
        self.capture_active = False

        self.title("Assign a Key Sound")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(app.root)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<KeyPress>", self._on_key_press)

        # The global listener must not play sounds while the assignment dialog is active.
        self.app.keyboard_service.pause()

        try:
            if app.icon_img is not None and not sys.platform.startswith("win"):
                self.iconphoto(False, app.icon_img)
            elif sys.platform.startswith("win") and ICON_ICO.exists():
                self.iconbitmap(str(ICON_ICO))
        except Exception:
            pass

        w, h = 620, 650
        r = app.root
        r.update_idletasks()
        x = r.winfo_rootx() + max(0, (r.winfo_width() - w) // 2)
        y = r.winfo_rooty() + max(0, (r.winfo_height() - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        f = app.font
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=28, pady=(22, 12))
        tk.Label(header, text="Assign a Key Sound", font=f(22, "bold"), fg=INK, bg=BG).pack(anchor="w")
        tk.Label(header, text="Make one keyboard key play a different sound.",
                 font=f(10), fg=MUTED, bg=BG).pack(anchor="w", pady=(4, 0))

        # Key section
        key_card = Card(self, outer=BG)
        key_card.pack(fill="x", padx=28)
        ki = key_card.inner
        top = tk.Frame(ki, bg=CARD)
        top.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(top, text="1  Choose a key", font=f(11, "bold"), fg=INK, bg=CARD).pack(side="left")
        self.capture_btn = Pill(
            top, "Press a key", self.start_capture, f(9, "bold"),
            outer=CARD, fill=ACCENT if key is None else SOFT,
            hover=ACCENT_HOVER if key is None else SOFT_HOVER, padx=14, pady=6
        )
        self.capture_btn.pack(side="right")

        self.key_stage = tk.Frame(ki, bg=CARD)
        self.key_stage.pack(fill="x", padx=16, pady=(0, 14))

        # Sound section
        sound_header = tk.Frame(self, bg=BG)
        sound_header.pack(fill="x", padx=28, pady=(16, 7))
        tk.Label(sound_header, text="2  Choose a sound", font=f(11, "bold"), fg=INK, bg=BG).pack(side="left")
        tk.Label(sound_header, text="This changes only the selected key", font=f(9), fg=MUTED, bg=BG).pack(side="right")

        list_card = Card(self, outer=BG)
        list_card.pack(fill="x", padx=28)
        holder = tk.Frame(list_card.inner, bg=CARD, height=190)
        holder.pack(fill="x")
        holder.pack_propagate(False)
        self.sf = ScrollFrame(holder, CARD)
        self.sf.pack(fill="both", expand=True)

        # Bottom actions
        bar = tk.Frame(self, bg=BG)
        bar.pack(side="bottom", fill="x", padx=28, pady=(12, 20))
        left = tk.Frame(bar, bg=BG)
        left.pack(side="left", fill="x", expand=True)
        self.selected_label = tk.Label(left, text="", font=f(9), fg=MUTED, bg=BG)
        self.selected_label.pack(side="left")
        Pill(bar, "Cancel", self.close, f(9, "bold"), outer=BG,
             fill=SOFT, hover=SOFT_HOVER, padx=15, pady=7).pack(side="right")
        self.save_btn = Pill(bar, "Assign sound", None, f(9, "bold"), outer=BG,
                              fill=SOFT, fg=MUTED, hover=SOFT, padx=18, pady=7)
        self.save_btn.pack(side="right", padx=(0, 8))

        self.render_key()
        self.render_sounds()
        self._update_save_state()
        self.after(20, self._finish_layout)

        try:
            self.grab_set()
            self.focus_force()
        except Exception:
            pass

    def _finish_layout(self):
        if self.winfo_exists():
            for card in self.winfo_children():
                if isinstance(card, Card):
                    card.resize_to_content()
            self.update_idletasks()

    def start_capture(self):
        if self.capture_active:
            return
        self.capture_active = True
        self.app.keyboard_service.pause()
        self.capture_btn.restyle(ACCENT, ACCENT_HOVER, INK, self.cancel_capture)
        self.render_key()
        self.focus_force()

    def _on_key_press(self, event):
        if not self.capture_active:
            return
        kid = tk_key_id(event)
        if not kid:
            return
        self.set_key(kid)
        return "break"

    def set_key(self, kid):
        if not kid or not self.capture_active:
            return
        self.key = kid
        self.capture_active = False
        self.capture_btn.restyle(SOFT, SOFT_HOVER, INK, self.start_capture)
        self.render_key()
        self._update_save_state()
        self.focus_force()

    def cancel_capture(self):
        self.capture_active = False
        self.capture_btn.restyle(SOFT, SOFT_HOVER, INK, self.start_capture)
        self.render_key()
        self._update_save_state()
        self.focus_force()

    def render_key(self):
        for child in self.key_stage.winfo_children():
            child.destroy()
        f = self.app.font
        if self.capture_active:
            cap, title, sub = "…", "Listening for one key", "Press the key you want to customize now."
        elif self.key:
            cap, title, sub = pretty_key(self.key), "Key selected", "You can press Change key if you want another key."
        else:
            cap, title, sub = "?", "No key selected", "Click Press a key, then press the keyboard key you want to customize."

        make_keycap(self.key_stage, cap, CARD, f(20, "bold"), scale=1.35).pack(pady=(3, 3))
        tk.Label(self.key_stage, text=title, font=f(10, "bold"), fg=INK, bg=CARD).pack()
        tk.Label(self.key_stage, text=sub, font=f(9), fg=MUTED, bg=CARD,
                 wraplength=500, justify="center").pack(pady=(2, 4))
        if self.capture_active:
            Pill(self.key_stage, "Cancel", self.cancel_capture, f(8, "bold"),
                 outer=CARD, fill=SOFT, hover=SOFT_HOVER, padx=10, pady=4).pack()

    def render_sounds(self):
        inner = self.sf.inner
        for child in inner.winfo_children():
            child.destroy()
        f = self.app.font
        for name, path, preset in self.app.available_sounds():
            selected = same_path(path, self.sound)
            bg = SELECTED_ROW if selected else CARD
            row = tk.Frame(inner, bg=bg, cursor="hand2")
            row.pack(fill="x", padx=5, pady=3)
            radio = tk.Canvas(row, width=25, height=25, bg=bg, highlightthickness=0)
            radio.pack(side="left", padx=(11, 9), pady=8)
            radio.create_oval(3, 3, 22, 22, outline=ACCENT_DEEP if selected else BORDER, width=2)
            if selected:
                radio.create_oval(7, 7, 18, 18, fill=ACCENT_DEEP, outline="")
            info = tk.Frame(row, bg=bg)
            info.pack(side="left", fill="x", expand=True, pady=7)
            tk.Label(info, text=name, font=f(10, "bold"), fg=INK, bg=bg).pack(anchor="w")
            tk.Label(info, text="Included with Faaaaaah" if preset else "Custom sound",
                     font=f(8), fg=MUTED, bg=bg).pack(anchor="w")
            Pill(row, "▶ Preview", lambda p=str(path): self.app.preview_path(p), f(8, "bold"),
                 outer=bg, fill=SOFT, hover=SOFT_HOVER, padx=8, pady=4).pack(side="right", padx=(4, 10))
            for widget in (row, radio, info, *info.winfo_children()):
                widget.bind("<Button-1>", lambda _e, p=str(path): self.pick_sound(p))

    def pick_sound(self, path):
        self.sound = str(path)
        self.render_sounds()
        self._update_save_state()

    def _update_save_state(self):
        ready = bool(self.key and self.sound) and not self.capture_active
        self.save_btn.restyle(
            ACCENT if ready else SOFT,
            ACCENT_HOVER if ready else SOFT,
            INK if ready else MUTED,
            self._save if ready else None,
        )
        if self.sound:
            self.selected_label.config(text=f"Sound: {self.app.sound_name(self.sound)}")
        else:
            self.selected_label.config(text="No sound selected")

    def _save(self):
        if not self.key or not self.sound or self.capture_active:
            return
        self.app.assign_key(self.key, self.sound)
        self.close()

    def close(self):
        self.capture_active = False
        self.app.keyboard_service.resume()
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
