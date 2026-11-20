"""Comprehensive 11-layout engine supporting vertical (9:16), square (1:1), portrait (4:5),
landscape (16:9), and 3:4 aspect ratios, circle cameras, picture-in-picture, and split views."""
import math

CATALOG = [
    ('stack', 'Face + gameplay', 'Camera above the action'),
    ('bottom', 'Gameplay + face', 'Camera below the action'),
    ('blur', 'Blurred fill', 'Keep the complete source'),
    ('fill', 'Fill screen', 'Full-frame centre crop'),
    ('game', 'Gameplay only', 'Use your selected game area'),
    ('pip_tl', 'Camera top-left', 'Floating selected facecam'),
    ('pip_tr', 'Camera top-right', 'Floating selected facecam'),
    ('pip_bl', 'Camera bottom-left', 'Floating selected facecam'),
    ('pip_br', 'Camera bottom-right', 'Floating selected facecam'),
    ('circle', 'Circle camera', 'Round facecam above gameplay'),
    ('side', 'Side by side', 'Camera and gameplay columns'),
]

LAYOUT_DICT = {key: name for key, name, _ in CATALOG}

ASPECTS = {
    'vertical': (1080, 1920),
    'square': (1080, 1080),
    'portrait': (1080, 1350),
    'landscape': (1920, 1080),
    'threefour': (1080, 1440),
}


def output_settings(body: dict) -> tuple:
    """Return (width, height, fps) based on aspect ratio and resolution setting."""
    aspect = str(body.get('aspect', 'vertical'))
    if aspect not in ASPECTS:
        raise ValueError('Choose a supported aspect ratio: vertical, square, portrait, landscape, or threefour.')
    resolution = int(body.get('resolution', 1080))
    fps = int(body.get('fps') or 0)
    if resolution not in (720, 1080, 2160) or fps not in (0, 24, 30, 60):
        raise ValueError('Choose 720, 1080 or 2160 and a supported frame rate.')
    width, height = ASPECTS[aspect]
    scale = resolution / 1080
    return int(width * scale) // 2 * 2, int(height * scale) // 2 * 2, fps


def text_positions(name: str, top: float = 0.38, caption_y: int = 880, width: int = 1080, height: int = 1920) -> dict:
    """Calculate where the hook title and subtitles should sit in the layout."""
    spec = geometry(name, top, width, height)
    cam = next((layer for layer in spec['layers'] if layer.get('source') == 'cam'), None)
    hook_y = 200 * height / 1920
    position = caption_y * height / 1920
    if cam and cam['y'] < 100 * height / 1920:
        hook_y = cam['y'] + cam['h'] + 30 * height / 1920
    if name == 'side':
        hook_y = 200 * height / 1920
    if caption_y == 880 and cam and cam['y'] > 900 * height / 1920:
        position = min(position, cam['y'] - 120 * height / 1920)
    return {'hook_y': round(hook_y), 'caption_y': round(position)}


def geometry(name: str, top: float = 0.38, width: int = 1080, height: int = 1920) -> dict:
    """Determine layer dimensions and placement coordinates for the selected layout."""
    valid_names = {x[0] for x in CATALOG}
    if name not in valid_names:
        # Fallback mapping for legacy names
        mapping = {'crop': 'fill', 'split': 'stack', 'split_tr': 'pip_tr', 'split_tl': 'pip_tl',
                   'split_br': 'pip_br', 'split_bl': 'pip_bl', 'split_top': 'stack', 'zoom': 'blur'}
        name = mapping.get(name, 'blur')

    top = float(top)
    if not math.isfinite(top) or not 0.2 <= top <= 0.55:
        top = 0.38
    h = int(top * height) // 2 * 2
    full = {'source': 'full', 'x': 0, 'y': 0, 'w': width, 'h': height}
    game = {**full, 'source': 'game'}

    if name == 'blur':
        return {'mode': 'blur', 'layers': [], 'width': width, 'height': height}
    if name in ('fill', 'game'):
        layers = [full if name == 'fill' else game]
    elif name in ('stack', 'bottom'):
        cam = {'source': 'cam', 'x': 0, 'y': 0 if name == 'stack' else height - h, 'w': width, 'h': h}
        layers = [{**game, 'y': h if name == 'stack' else 0, 'h': height - h}, cam]
    elif name == 'side':
        w = int(top * width) // 2 * 2
        layers = [{**game, 'x': w, 'w': width - w}, {'source': 'cam', 'x': 0, 'y': 0, 'w': w, 'h': height}]
    else:
        # Picture in Picture and circle
        w = min(int(top * width) // 2 * 2, int(height * 0.45) // 2 * 2)
        size = w if name == 'circle' else int(w * 0.9) // 2 * 2
        margin = int(width * 36 / 1080) // 2 * 2
        layers = [
            game,
            {'source': 'cam',
             'x': width - w - margin if name in ('pip_tr', 'pip_br') else margin,
             'y': height - size - round(180 * height / 1920) if name in ('pip_bl', 'pip_br') else round(72 * height / 1920),
             'w': w, 'h': size, 'circle': name == 'circle'}
        ]
    return {'mode': 'layers', 'layers': layers, 'width': width, 'height': height}


def render_graph(name: str, rects: list = None, top: float = 0.38, width: int = 1080, height: int = 1920,
                 fps: int = 30) -> str:
    """Generate FFmpeg filter complex graph for any of the 11 native layouts."""
    spec = geometry(name, top, width, height)
    if rects is None or len(rects) < 2:
        # Default rects: cam in top-right, game full
        rects = [(0.60, 0.0, 0.40, 0.55), (0.0, 0.0, 1.0, 1.0)]

    if spec['mode'] == 'blur':
        bw, bh = max(2, width // 8 * 2), max(2, height // 8 * 2)
        return (f"[0:v]setpts=PTS-STARTPTS,fps={fps},split=2[b][f];"
                f"[b]scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},boxblur=8:2,scale={width}:{height},eq=brightness=-0.14:saturation=1.15[bg];"
                f"[f]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v0];")

    layers = spec['layers']
    parts = []
    if len(layers) > 1:
        parts.append(f"[0:v]setpts=PTS-STARTPTS,fps={fps},split={len(layers)}" + ''.join(f"[s{i}]" for i in range(len(layers))))
    else:
        parts.append(f"[0:v]setpts=PTS-STARTPTS,fps={fps}[s0]")

    for i, layer in enumerate(layers):
        source = f"[s{i}]"
        crop = ''
        if layer['source'] != 'full':
            rc = rects[0 if layer['source'] == 'cam' else 1]
            if isinstance(rc[0], float) and rc[0] <= 1.0:
                # Relative fraction coordinates
                rx, ry, rw, rh = rc
                crop = f"crop=w=iw*{rw:.2f}:h=ih*{rh:.2f}:x=iw*{rx:.2f}:y=ih*{ry:.2f},"
            else:
                x, y, w, h = rc
                crop = f"crop={w}:{h}:{x}:{y},"

        w, h = layer['w'], layer['h']
        mask = ''
        if layer.get('circle'):
            mask = ",format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(min(W,H)/2,2)),255,0)'"
        parts.append(source + crop + f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1" + mask + f"[p{i}]")

    first = layers[0]
    parts.append(f"[p0]pad={width}:{height}:{first['x']}:{first['y']}:black[b0]")
    for i, layer in enumerate(layers[1:], 1):
        parts.append(f"[b{i-1}][p{i}]overlay={layer['x']}:{layer['y']}:shortest=1[b{i}]")

    # Divider bar for stack / bottom
    if name in ('stack', 'bottom'):
        div_y = int(top * height) - 2 if name == 'stack' else height - int(top * height) - 2
        parts.append(f"[b{len(layers)-1}]drawbox=x=0:y={div_y}:w={width}:h=4:color=0xFF8B33@0.9:t=fill[v0];")
    else:
        parts.append(f"[b{len(layers)-1}]null[v0];")

    return ';'.join(parts)
