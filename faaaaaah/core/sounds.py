import shutil
from pathlib import Path
from .config import SOUNDS_DIR, PRESET_SOUND, PRESET_NAME, ensure_user_dirs
from .keys import same_path

class SoundLibrary:
    def __init__(self, audio, show_error=None):
        self.audio = audio
        self.show_error = show_error or (lambda _msg: None)

    def available(self):
        items = [(PRESET_NAME, str(PRESET_SOUND), True)]
        try:
            files = sorted((p for p in SOUNDS_DIR.iterdir() if p.suffix.lower() in (".mp3", ".wav")), key=lambda p: p.name.lower())
        except Exception:
            files = []
        return items + [(p.stem, str(p), False) for p in files]

    @staticmethod
    def name(path):
        return PRESET_NAME if same_path(path, PRESET_SOUND) else Path(path).stem

    def import_file(self, source):
        source = Path(source)
        if source.suffix.lower() not in (".mp3", ".wav"):
            self.show_error("Please choose an MP3 or WAV sound.")
            return None
        target = SOUNDS_DIR / source.name
        if target.exists():
            i = 2
            while target.exists():
                target = SOUNDS_DIR / f"{source.stem} ({i}){source.suffix}"
                i += 1
        try:
            ensure_user_dirs()
            shutil.copy2(source, target)
            if self.audio.available and self.audio.get(target) is None:
                self.show_error(
                    "The sound was added, but Faaaaaah could not decode it. "
                    "Try a standard MP3 or WAV file."
                )
            return target
        except Exception as exc:
            self.show_error(f"Could not add this sound.\n\n{exc}")
            return None
