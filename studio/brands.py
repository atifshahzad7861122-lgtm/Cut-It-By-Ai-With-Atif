"""Caption styling branding presets. Saved locally in data/preferences."""
import json
import math
import re
import threading
from pathlib import Path

KEYS = ('caption_font', 'caption_size', 'caption_color', 'caption_active', 'caption_outline', 'caption_max_words')
FONTS = ('Poppins ExtraBold', 'Anton', 'Archivo Black', 'Arial', 'Impact', 'Verdana', 'Georgia', 'Nirmala UI')


def appearance(body: dict) -> dict:
    result = {}
    for key in KEYS:
        value = body.get(key)
        if value in (None, ''):
            continue
        if key == 'caption_font':
            if not isinstance(value, str) or not re.fullmatch(r'[\w -]{1,80}', value):
                raise ValueError('Use a font family name with letters, numbers, spaces or hyphens.')
        elif key in ('caption_color', 'caption_active', 'caption_outline'):
            if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
                raise ValueError('Choose a six-digit caption colour (e.g. #FF8B33).')
            value = value.upper()
        else:
            value = float(value)
            lo, hi = (24, 180) if key == 'caption_size' else (1, 12)
            if not math.isfinite(value) or not lo <= value <= hi or value != int(value):
                raise ValueError('Caption size must be 24–180; group size 1–12.')
            value = int(value)
        result[key] = value
    return result


def load_profiles(prefs_dir: Path) -> dict:
    p = prefs_dir / 'caption-brands.json'
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_profile(prefs_dir: Path, name: str, settings: dict) -> dict:
    prefs_dir.mkdir(parents=True, exist_ok=True)
    p = prefs_dir / 'caption-brands.json'
    profiles = load_profiles(prefs_dir)
    config = appearance(settings)
    if not config:
        raise ValueError('Choose at least one custom caption setting.')
    profiles[name] = config
    p.write_text(json.dumps(profiles, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'name': name, 'settings': config}
