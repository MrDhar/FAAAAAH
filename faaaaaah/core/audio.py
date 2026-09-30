try:
    import pygame
except ImportError:
    pygame = None

class AudioEngine:
    def __init__(self, volume=0.8, enabled=True, on_error=None):
        self.volume = volume
        self.enabled = enabled
        self.cache = {}
        self.current = None
        self.on_error = on_error or (lambda _msg: None)

    @property
    def available(self):
        return pygame is not None

    def start(self):
        if pygame is None:
            self.on_error("Audio library missing")
            return False
        try:
            pygame.mixer.pre_init(44100, -16, 2, 256)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
            return True
        except Exception:
            self.on_error("Could not start audio")
            return False

    def get(self, path):
        path = str(path)
        if path in self.cache:
            return self.cache[path]
        if pygame is None:
            return None
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.volume)
        except Exception:
            sound = None
        self.cache[path] = sound
        return sound

    def load(self, path):
        sound = self.get(path)
        if sound is None:
            self.cache.pop(str(path), None)
            return False
        self.current = sound
        return True

    def play(self, sound=None):
        if not self.enabled or sound is None or pygame is None:
            return
        try:
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(sound)
        except Exception:
            pass

    def play_path(self, path):
        sound = self.get(path)
        self.play(sound)

    def set_volume(self, value):
        self.volume = max(0.0, min(1.0, float(value)))
        for sound in self.cache.values():
            if sound is not None:
                sound.set_volume(self.volume)

    def stop(self):
        if pygame is not None:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
