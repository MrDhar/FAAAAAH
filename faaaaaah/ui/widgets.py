import tkinter as tk
from tkinter import font as tkfont

from faaaaaah.core.config import (
    ACCENT, ACCENT_DEEP, ACCENT_HOVER, BG, BORDER, CARD, INK,
    NAV_HOVER, SHADOW, SIDEBAR,
)

def rr(x1, y1, x2, y2, r):
    """Points for a smooth rounded rectangle polygon."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return [x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y1 + r,
            x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1]


def lerp_color(a, b, t):
    ar, ag, ab = (int(a[i:i + 2], 16) for i in (1, 3, 5))
    br, bg, bb = (int(b[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(ar + (br - ar) * t), int(ag + (bg - ag) * t), int(ab + (bb - ab) * t))


class Card(tk.Canvas):
    """Rounded, softly shadowed surface. Put content in `.inner`."""

    def __init__(self, parent, outer=BG, fill=CARD, radius=18, pad=10):
        super().__init__(parent, bg=outer, highlightthickness=0, bd=0, height=10)
        self.fill, self.radius, self.pad = fill, radius, pad
        self.inner = tk.Frame(self, bg=fill)
        self.create_window(pad, pad, window=self.inner, anchor="nw", tags="win")
        self.bind("<Configure>", self._layout)
        self.inner.bind("<Configure>", self._inner_changed)

    def resize_to_content(self):
        """Recalculate the card height after dynamic children are added/removed."""
        self.update_idletasks()
        self._inner_changed()
        self.update_idletasks()

    def _inner_changed(self, _e=None):
        h = self.inner.winfo_reqheight() + 2 * self.pad + 3
        if int(float(self.cget("height"))) != h:
            self.config(height=h)

    def _layout(self, _e=None):
        w, h = self.winfo_width(), self.winfo_height()
        self.delete("bg")
        self.create_polygon(rr(1, 3, w - 1, h - 1, self.radius), smooth=True, fill=SHADOW, outline="", tags="bg")
        self.create_polygon(rr(1, 1, w - 1, h - 3, self.radius), smooth=True, fill=self.fill, outline=BORDER, tags="bg")
        self.tag_lower("bg")
        self.itemconfigure("win", width=max(1, w - 2 * self.pad), height=max(1, h - 2 * self.pad - 3))


class Pill(tk.Canvas):
    """Reusable modern button with hover, press and disabled states."""

    def __init__(self, parent, text, command=None, font=None, outer=CARD, fill=ACCENT, fg=INK,
                 hover=ACCENT_HOVER, padx=18, pady=8, min_w=0):
        f = tkfont.Font(font=font)
        w = max(f.measure(text) + 2 * padx, min_w)
        h = f.metrics("linespace") + 2 * pady
        super().__init__(
            parent,
            width=w,
            height=h,
            bg=outer,
            highlightthickness=0,
            bd=0,
            cursor="hand2" if command else "",
            takefocus=1 if command else 0,
        )
        self.outer = outer
        self.command = command
        self.fill = fill
        self.hover = hover
        self.fg = fg
        self._hovered = False
        self._pressed = False

        # A tiny offset shadow gives the button a physical, tactile feel without
        # making the otherwise-flat UI look heavy.
        self.create_polygon(
            rr(1, 3, w - 1, h - 1, h / 2),
            smooth=True,
            fill=SHADOW,
            outline="",
            tags="shadow",
        )
        self.create_polygon(
            rr(1, 1, w - 1, h - 3, h / 2),
            smooth=True,
            fill=fill,
            outline=fill,
            tags="shape",
        )
        self.create_text(w / 2, (h / 2) - 1, text=text, fill=fg, font=font, tags="label")
        self._bind_command(command)

    def _bind_command(self, command):
        self.unbind("<Enter>")
        self.unbind("<Leave>")
        self.unbind("<ButtonPress-1>")
        self.unbind("<ButtonRelease-1>")
        self.unbind("<FocusIn>")
        self.unbind("<FocusOut>")
        self.unbind("<Return>")
        self.unbind("<space>")
        self.command = command
        self._hovered = False
        self._pressed = False
        enabled = command is not None
        self.config(cursor="hand2" if enabled else "", takefocus=1 if enabled else 0)
        if enabled:
            self.bind("<Enter>", self._enter)
            self.bind("<Leave>", self._leave)
            self.bind("<ButtonPress-1>", self._press)
            self.bind("<ButtonRelease-1>", self._release)
            self.bind("<FocusIn>", lambda _e: self._paint(self.hover))
            self.bind("<FocusOut>", lambda _e: self._paint(self.fill))
            self.bind("<Return>", lambda _e: self._click())
            self.bind("<space>", lambda _e: self._click())
        self._paint(self.fill if enabled else self.fill)
        self.itemconfigure("label", fill=self.fg)
        self.itemconfigure("shadow", fill=SHADOW if enabled else BORDER)

    def _enter(self, _e=None):
        self._hovered = True
        if not self._pressed:
            self._paint(self.hover)

    def _leave(self, _e=None):
        self._hovered = False
        self._pressed = False
        self._paint(self.fill)

    def _press(self, _e=None):
        if not self.command:
            return
        self._pressed = True
        self._paint(self.fill)
        self.coords("shape", *rr(1, 3, self.winfo_width() - 1, self.winfo_height() - 1, self.winfo_height() / 2))
        self.coords("label", self.winfo_width() / 2, self.winfo_height() / 2)

    def _release(self, _e=None):
        if not self.command:
            return
        was_pressed = self._pressed
        self._pressed = False
        self._paint(self.hover if self._hovered else self.fill)
        self.coords("shape", *rr(1, 1, self.winfo_width() - 1, self.winfo_height() - 3, self.winfo_height() / 2))
        self.coords("label", self.winfo_width() / 2, (self.winfo_height() / 2) - 1)
        if was_pressed:
            self._click()

    def _paint(self, color):
        self.itemconfigure("shape", fill=color, outline=color)

    def _click(self):
        if self.command:
            self.command()

    def restyle(self, fill, hover, fg, command):
        self.fill, self.hover, self.fg = fill, hover, fg
        self._paint(fill)
        self.itemconfigure("label", fill=fg)
        self._bind_command(command)


def make_keycap(parent, text, bg, font, scale=1.0):
    f = tkfont.Font(font=font)
    w = max(int(46 * scale), f.measure(text) + int(28 * scale))
    h = int(40 * scale)
    c = tk.Canvas(parent, width=w, height=h + 4, bg=bg, highlightthickness=0, bd=0)
    c.create_polygon(rr(1, 4, w - 1, h + 3, 10 * scale), smooth=True, fill="#C9CEDA", outline="")
    c.create_polygon(rr(1, 1, w - 1, h - 1, 10 * scale), smooth=True, fill="#FFFFFF", outline="#D5D9E3")
    c.create_text(w / 2, h / 2, text=text, font=font, fill=INK)
    return c


class Toggle(tk.Canvas):
    """macOS-style switch with a smooth slide."""
    W, H = 58, 34

    def __init__(self, parent, on, command, bg):
        super().__init__(parent, width=self.W, height=self.H, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self.t = 1.0 if on else 0.0
        self.target = self.t
        self.create_line(17, 17, 41, 17, width=30, capstyle="round", fill=ACCENT, tags="track")
        self.create_oval(0, 0, 0, 0, fill="#C9CDD6", outline="", tags="shadow")
        self.create_oval(0, 0, 0, 0, fill="#FFFFFF", outline="", tags="knob")
        self._draw()
        self.bind("<Button-1>", lambda _e: command())

    def _draw(self):
        x = 17 + 24 * self.t
        self.itemconfigure("track", fill=lerp_color("#D3D7E0", ACCENT, self.t))
        self.coords("shadow", x - 13, 5, x + 13, 33)
        self.coords("knob", x - 13, 4, x + 13, 30)

    def set(self, on):
        self.target = 1.0 if on else 0.0
        self._step()

    def _step(self):
        if abs(self.target - self.t) < 0.02:
            self.t = self.target
            self._draw()
            return
        self.t += (self.target - self.t) * 0.4
        self._draw()
        self.after(14, self._step)


class VolumeSlider(tk.Canvas):
    """Light, responsive slider. Drawn with a few canvas items whose coords are moved directly."""
    H, PAD, TRACK = 44, 18, 8

    def __init__(self, parent, value, on_change, on_release, bg=CARD):
        super().__init__(parent, height=self.H, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self.value, self.on_change, self.on_release = value, on_change, on_release
        self.hover = self.drag = False
        self.bind("<Configure>", lambda _e: self._build())
        self.bind("<Button-1>", self._press)
        self.bind("<B1-Motion>", self._move)
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<Enter>", lambda _e: self._state(hover=True))
        self.bind("<Leave>", lambda _e: self._state(hover=False))

    def _build(self):
        self.delete("all")
        w, y = self.winfo_width(), self.H / 2
        self.create_line(self.PAD, y, w - self.PAD, y, width=self.TRACK, capstyle="round", fill="#DDE1EA", tags="track")
        self.create_line(self.PAD, y, self.PAD, y, width=self.TRACK, capstyle="round", fill=ACCENT, tags="fill")
        self.create_oval(0, 0, 0, 0, fill="#D2D6E0", outline="", tags="shadow")
        self.create_oval(0, 0, 0, 0, fill=ACCENT_DEEP, outline="#FFFFFF", width=3, tags="knob")
        self._place()

    def _state(self, hover=None, drag=None):
        if hover is not None:
            self.hover = hover
        if drag is not None:
            self.drag = drag
        self._place()

    def _place(self):
        w, y = self.winfo_width(), self.H / 2
        if w <= 1:
            return
        x0, x1 = self.PAD, w - self.PAD
        x = x0 + (x1 - x0) * self.value
        r = 14 if self.drag else 12
        knob = "#FF8A00" if self.drag else (ACCENT_HOVER if self.hover else ACCENT_DEEP)
        fill = "#FFB000" if self.drag else ACCENT
        self.coords("fill", x0, y, x, y)
        self.itemconfigure("fill", fill=fill)
        self.coords("shadow", x - r - 1, y - r + 2, x + r + 1, y + r + 2)
        self.coords("knob", x - r, y - r, x + r, y + r)
        self.itemconfigure("knob", fill=knob)

    def _from_event(self, e):
        w = self.winfo_width()
        span = max(1, w - 2 * self.PAD)
        self.value = max(0.0, min(1.0, (e.x - self.PAD) / span))
        self._place()
        self.on_change(self.value)

    def _press(self, e):
        self.drag = True
        self._from_event(e)

    def _move(self, e):
        self._from_event(e)

    def _release(self, _e):
        self.drag = False
        self._place()
        self.on_release()


class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, yscrollincrement=24)
        self.canvas.pack(fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda _e: self._update())
        self.canvas.bind("<Configure>", self._canvas_changed)

    def _canvas_changed(self, e):
        self.canvas.itemconfigure(self.win, width=e.width)
        self._update()

    def _update(self):
        h = max(self.inner.winfo_reqheight(), self.canvas.winfo_height())
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), h))

    def scroll(self, units):
        if self.inner.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(units, "units")


class NavItem(tk.Canvas):
    W, H = 204, 42

    def __init__(self, parent, text, kind, color, command, font):
        super().__init__(parent, width=self.W, height=self.H, bg=SIDEBAR, highlightthickness=0, bd=0, cursor="hand2")
        self.text, self.kind, self.color, self.font = text, kind, color, font
        self.selected = self.hover = False
        self.bind("<Button-1>", lambda _e: command())
        self.bind("<Enter>", lambda _e: self._set(hover=True))
        self.bind("<Leave>", lambda _e: self._set(hover=False))
        self.draw()

    def _set(self, hover=None, selected=None):
        if hover is not None:
            self.hover = hover
        if selected is not None:
            self.selected = selected
        self.draw()

    def draw(self):
        self.delete("all")
        if self.selected:
            self.create_polygon(rr(1, 1, self.W - 1, self.H - 1, 12), smooth=True, fill=ACCENT, outline=ACCENT)
        elif self.hover:
            self.create_polygon(rr(1, 1, self.W - 1, self.H - 1, 12), smooth=True, fill=NAV_HOVER, outline=NAV_HOVER)
        x, y, s = 12, 9, 24
        self.create_polygon(rr(x, y, x + s, y + s, 7), smooth=True, fill=self.color, outline=self.color)
        cx, cy = x + s / 2, y + s / 2
        if self.kind == "keys":
            self.create_polygon(rr(cx - 7, cy - 5, cx + 7, cy + 5, 3), smooth=True, fill="#FFFFFF", outline="#FFFFFF")
            self.create_line(cx - 3, cy, cx + 3, cy, fill=self.color, width=2, capstyle="round")
        else:
            self.create_text(cx, cy, text="\u266a" if self.kind == "home" else "\u2261", fill="#FFFFFF",
                             font=(self.font[0], 12, "bold"))
        self.create_text(50, self.H / 2, text=self.text, anchor="w", fill=INK, font=self.font)


# ---------- assign-a-key dialog ----------
