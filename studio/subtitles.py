"""Subtitle parsing, validation, and SRT / WebVTT export and import."""
import html
import math
import re


def _seconds(value: str) -> float:
    value = value.strip().replace(',', '.')
    parts = value.split(':')
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = '0', parts[0], parts[1]
    else:
        raise ValueError('Bad time: ' + value)
    h, m, s = int(h), int(m), float(s)
    if h < 0 or not 0 <= m < 60 or not math.isfinite(s) or not 0 <= s < 60:
        raise ValueError('Invalid subtitle timestamp.')
    return h * 3600 + m * 60 + s


def validate_track(items: list, duration: float = None, allow_overlap: bool = False) -> list:
    previous = 0.0
    if not isinstance(items, list) or not items or len(items) > 10000:
        raise ValueError('Provide between 1 and 10000 subtitle cues.')
    result = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f'Cue {index+1} must be an object.')
        start, end = float(item['start']), float(item['end'])
        text = str(item.get('text', item.get('w', '')))
        if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end <= start:
            raise ValueError(f'Cue {index+1} has invalid times.')
        if not allow_overlap and start < previous - 0.001:
            start = previous
            if end <= start:
                end = start + 0.5
        if duration is not None and end > duration + 0.1:
            end = min(end, duration)
        if not text.strip():
            continue
        result.append({'start': round(start, 3), 'end': round(end, 3), 'text': text})
        previous = end
    return result


def parse_track(text: str, allow_overlap: bool = False) -> list:
    """Strict SRT/WebVTT track import; preserve explicit cue line breaks and Unicode."""
    text = str(text).lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
    items = []
    for block in re.split(r'\n\s*\n', text.strip()):
        lines = block.splitlines()
        if lines and lines[0].startswith(('NOTE', 'STYLE', 'REGION', 'WEBVTT')):
            lines = [l for l in lines if not l.startswith(('NOTE', 'STYLE', 'REGION', 'WEBVTT'))]
        for index, line in enumerate(lines):
            if '-->' not in line:
                continue
            left, right = line.split('-->', 1)
            try:
                start = _seconds(left.strip())
                end = _seconds(right.strip().split()[0])
            except (ValueError, IndexError):
                continue
            clean = '\n'.join(html.unescape(re.sub(r'<[^>]+>', '', l)).strip() for l in lines[index + 1:])
            if clean:
                items.append({'start': start, 'end': end, 'text': clean})
            break
    return validate_track(items, allow_overlap=allow_overlap)


def write_track(items: list, format: str = 'srt', shift: float = 0.0, duration: float = None) -> str:
    """Export subtitle cues into SRT or WebVTT format."""
    if format not in ('srt', 'vtt'):
        raise ValueError('Choose srt or vtt.')
    shift = float(shift or 0.0)

    # Format into words / items
    cues = []
    for it in items:
        s = float(it.get('start', it.get('s', 0))) + shift
        e = float(it.get('end', it.get('e', s + 0.5))) + shift
        t = it.get('text', it.get('w', ''))
        if t:
            cues.append({'start': s, 'end': e, 'text': t})

    cues = validate_track(cues, duration=duration, allow_overlap=True)

    def stamp(value: float) -> str:
        ms = round(value * 1000)
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds, ms = divmod(ms, 1000)
        sep = ',' if format == 'srt' else '.'
        return f'{hours:02}:{minutes:02}:{seconds:02}{sep}{ms:03}'

    blocks = []
    for index, item in enumerate(cues, 1):
        prefix = f"{index}\n" if format == 'srt' else ""
        blocks.append(f"{prefix}{stamp(item['start'])} --> {stamp(item['end'])}\n{item['text']}")

    header = 'WEBVTT\n\n' if format == 'vtt' else ''
    return header + '\n\n'.join(blocks) + '\n'


def cues_to_words(cues_list: list) -> list:
    """Spread multi-word cues into approximate word-level timestamps based on letter lengths."""
    words = []
    for cue in cues_list:
        text = str(cue.get('text', '')).strip()
        tokens = text.split()
        if not tokens:
            continue
        total_chars = sum(len(w) for w in tokens)
        start, end = cue['start'], cue['end']
        dur = max(0.2, end - start)
        cur_t = start
        for w in tokens:
            w_dur = dur * (len(w) / max(1, total_chars))
            w_start = round(cur_t, 3)
            w_end = round(cur_t + w_dur, 3)
            words.append({'w': w, 's': w_start, 'e': w_end, 'text': w, 'start': w_start, 'end': w_end})
            cur_t += w_dur
    return words
