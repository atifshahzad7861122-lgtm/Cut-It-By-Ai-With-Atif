"""Visual styling extras for exports: social card templates, background cards,
watermark positioning, and outro ribbons."""
import math
import re
from pathlib import Path

KEYS = (
    'template', 'tpl_name', 'tpl_handle', 'bg_mode', 'bg_color', 'bg_color2', 'bg_image',
    'bg_dim', 'bg_blur', 'padding', 'radius', 'watermark_image', 'watermark_pos',
    'watermark_size', 'watermark_opacity', 'credit', 'outro_text', 'outro_seconds'
)
TEMPLATES = ('none', 'x_light', 'x_dark', 'tiktok_hook', 'breaking_news')
BG_MODES = ('blur', 'color', 'gradient', 'image')
WM_POS = ('tl', 'tr', 'bl', 'br')
HEX = re.compile(r'^#[0-9a-fA-F]{6}$')


def hexcolor(value, default):
    value = default if value in (None, '') else str(value)
    if not HEX.match(value):
        raise ValueError('Colours must look like #RRGGBB.')
    return value


def ass_color(hex_, alpha=0):
    r, g, b = int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)
    return '&H%02X%02X%02X%02X&' % (alpha, b, g, r)


def rrect(x, y, w, h, r):
    """ASS drawing path of a rounded rectangle."""
    r = max(0, min(r, w / 2, h / 2))
    x, y, w, h, r = (round(v, 1) for v in (x, y, w, h, r))
    k = r * 0.5523
    return (f'm {x + r} {y} l {x + w - r} {y} b {x + w - r + k} {y} {x + w} {y + r - k} {x + w} {y + r} '
            f'l {x + w} {y + h - r} b {x + w} {y + h - r + k} {x + w - r + k} {y + h} {x + w - r} {y + h} '
            f'l {x + r} {y + h} b {x + r - k} {y + h} {x} {y + h - r + k} {x} {y + h - r} '
            f'l {x} {y + r} b {x} {y + r - k} {x + r - k} {y} {x + r} {y}')


def build_style_plan(options: dict, width: int = 1080, height: int = 1920) -> dict:
    """Build styling configurations for templates, backgrounds, and overlays."""
    template = options.get('template', 'none')
    if template not in TEMPLATES:
        template = 'none'

    bg_mode = options.get('bg_mode', 'blur')
    if bg_mode not in BG_MODES:
        bg_mode = 'blur'

    padding = int(options.get('padding', 0))
    radius = int(options.get('radius', 0))
    wm_pos = options.get('watermark_pos', 'br')
    if wm_pos not in WM_POS:
        wm_pos = 'br'

    wm_size = int(options.get('watermark_size', 96))
    wm_opacity = float(options.get('watermark_opacity', 0.4))

    return {
        'template': template,
        'tpl_name': str(options.get('tpl_name', '')),
        'tpl_handle': str(options.get('tpl_handle', '')),
        'bg_mode': bg_mode,
        'bg_color': hexcolor(options.get('bg_color'), '#1E1612'),
        'bg_color2': hexcolor(options.get('bg_color2'), '#FF8B33'),
        'padding': max(0, min(120, padding)),
        'radius': max(0, min(80, radius)),
        'watermark_pos': wm_pos,
        'watermark_size': max(48, min(240, wm_size)),
        'watermark_opacity': max(0.1, min(1.0, wm_opacity)),
        'credit': str(options.get('credit', ''))[:80],
        'outro_text': str(options.get('outro_text', ''))[:100],
        'outro_seconds': max(0, min(10, int(options.get('outro_seconds', 0))))
    }


def watermark_coordinates(pos: str, size: int, width: int = 1080, height: int = 1920) -> tuple:
    """Get (x, y) coordinates for watermark."""
    margin = 48
    if pos == 'tl':
        return margin, margin
    if pos == 'tr':
        return width - size - margin, margin
    if pos == 'bl':
        return margin, height - size - margin
    return width - size - margin, height - size - margin  # 'br'
