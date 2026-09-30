import json
import shutil
from pathlib import Path

from .config import CONFIG_FILE, PRESET_KEY, PRESET_SOUND, SOUNDS_DIR, ensure_user_dirs


class SettingsStore:
    @staticmethod
    def _is_preset(path):
        return path == PRESET_KEY or (path is not None and Path(path).resolve() == PRESET_SOUND.resolve())

    @staticmethod
    def _localize_sound(path):
        """Keep custom sounds inside Faaaaaah's private sound library."""
        if not path or SettingsStore._is_preset(path):
            return str(PRESET_SOUND), False
        source = Path(path)
        try:
            if source.resolve().parent == SOUNDS_DIR.resolve():
                return str(source), False
        except OSError:
            pass
        if not source.is_file():
            return None, False
        target = SOUNDS_DIR / source.name
        if target.resolve() != source.resolve() and target.exists():
            try:
                same = target.stat().st_size == source.stat().st_size
            except OSError:
                same = False
            if not same:
                i = 2
                while target.exists():
                    target = SOUNDS_DIR / f"{source.stem} ({i}){source.suffix}"
                    i += 1
        try:
            ensure_user_dirs()
            if not target.exists():
                shutil.copy2(source, target)
            return str(target), True
        except OSError:
            return None, False

    def load(self):
        data = {
            "sound_path": PRESET_KEY,
            "volume": 0.8,
            "enabled": True,
            "key_sounds": {},
            "key_sound_enabled": {},
        }
        try:
            if CONFIG_FILE.exists():
                raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    data.update(raw)
        except (OSError, ValueError, TypeError):
            pass

        migrated = False
        sound = data.get("sound_path")
        if self._is_preset(sound):
            data["sound_path"] = str(PRESET_SOUND)
        else:
            localized, changed = self._localize_sound(sound)
            data["sound_path"] = localized or str(PRESET_SOUND)
            migrated = migrated or changed

        try:
            volume = float(data.get("volume", 0.8))
        except (TypeError, ValueError):
            volume = 0.8
        data["volume"] = max(0.0, min(1.0, volume))

        enabled = data.get("enabled", True)
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() not in {"0", "false", "no", "off", ""}
        data["enabled"] = bool(enabled)

        raw_keys = data.get("key_sounds")
        raw_key_enabled = data.get("key_sound_enabled")
        cleaned = {}
        cleaned_enabled = {}
        if isinstance(raw_keys, dict):
            for kid, path in raw_keys.items():
                if not isinstance(kid, str) or not kid or not isinstance(path, (str, Path)):
                    continue
                if self._is_preset(path):
                    cleaned[kid] = str(PRESET_SOUND)
                else:
                    localized, changed = self._localize_sound(path)
                    if localized:
                        cleaned[kid] = localized
                        migrated = migrated or changed
                if isinstance(raw_key_enabled, dict):
                    value = raw_key_enabled.get(kid, True)
                    if isinstance(value, str):
                        value = value.strip().lower() not in {"0", "false", "no", "off", ""}
                    cleaned_enabled[kid] = bool(value)
                else:
                    cleaned_enabled[kid] = True
        data["key_sounds"] = cleaned
        data["key_sound_enabled"] = cleaned_enabled
        if migrated:
            self.save(data["sound_path"], data["volume"], data["enabled"], data["key_sounds"], data["key_sound_enabled"])
        return data

    def save(self, sound_path, volume, enabled, key_sounds, key_sound_enabled=None):
        try:
            ensure_user_dirs()
            localized_sound, _ = self._localize_sound(sound_path)
            if self._is_preset(sound_path):
                saved_sound = PRESET_KEY
            else:
                saved_sound = localized_sound or str(PRESET_SOUND)

            saved_keys = {}
            saved_key_enabled = {}
            key_sound_enabled = key_sound_enabled or {}
            for key, path in key_sounds.items():
                if self._is_preset(path):
                    saved_keys[key] = PRESET_KEY
                else:
                    localized, _ = self._localize_sound(path)
                    if localized:
                        saved_keys[key] = localized
                value = key_sound_enabled.get(key, True)
                if isinstance(value, str):
                    value = value.strip().lower() not in {"0", "false", "no", "off", ""}
                saved_key_enabled[key] = bool(value)

            payload = {
                "sound_path": saved_sound,
                "volume": max(0.0, min(1.0, float(volume))),
                "enabled": bool(enabled),
                "key_sounds": saved_keys,
                "key_sound_enabled": saved_key_enabled,
            }
            CONFIG_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except (OSError, TypeError, ValueError):
            pass
