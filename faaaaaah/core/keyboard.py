try:
    from pynput import keyboard
except ImportError:
    keyboard = None

from .keys import key_id


class KeyboardService:
    """Owns the single global keyboard listener used by Faaaaaah."""

    def __init__(self, on_key, on_error=None):
        self.on_key = on_key
        self.on_error = on_error or (lambda _msg: None)
        self.listener = None
        self.down = set()
        self.paused = False

    def start(self):
        if keyboard is None:
            self.on_error("Keyboard listener missing")
            return False
        if self.listener is not None:
            return True
        try:
            self.listener = keyboard.Listener(on_press=self._press, on_release=self._release)
            self.listener.daemon = True
            self.listener.start()
            return True
        except Exception as exc:
            self.listener = None
            self.on_error(f"Could not listen for keys: {exc}")
            return False

    def _release(self, key):
        self.down.discard(key)

    def _press(self, key):
        if key in self.down:
            return
        self.down.add(key)
        if self.paused:
            return
        self.on_key(key_id(key))

    def pause(self):
        self.paused = True
        self.down.clear()

    def resume(self):
        self.paused = False
        self.down.clear()

    def stop(self):
        self.pause()
        if self.listener is not None:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None
