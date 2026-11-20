"""Find the facecam box in a gameplay video locally without online AI.
Uses YuNet ONNX face detection when OpenCV is present, with automatic fallback
to edge / skin-tone quadrant detection.
"""
import subprocess
import tempfile
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

BW, BH = 640, 360          # frames kept for face detection
W, H = 320, 180            # frames used for the border search
FRAMES = 14
MODEL = Path(__file__).resolve().parent / 'models' / 'face_detection_yunet_2023mar.onnx'


def _duration(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                       capture_output=True, text=True, timeout=30)
    return float(r.stdout.strip() or 0)


def detect_facecam(video_path: Path) -> dict:
    """Detect streamer facecam bounding box (x, y, w, h) in fractions 0..1."""
    if cv2 is not None and MODEL.exists():
        try:
            return _detect_yunet(video_path)
        except Exception:
            pass
    # Fallback using PIL / numpy skin-tone analysis
    return _detect_fallback(video_path)


def _detect_yunet(video_path: Path) -> dict:
    dur = _duration(video_path)
    if dur <= 0:
        return {'found': False, 'quadrant': 'tr', 'rect': (0.60, 0.0, 0.40, 0.55)}

    lo, hi = dur * 0.06, dur * 0.94
    times = [lo + (hi - lo) * i / max(1, FRAMES - 1) for i in range(FRAMES)] if dur > 8 else [dur * (i + 0.5) / FRAMES for i in range(FRAMES)]

    detector = cv2.FaceDetectorYN.create(str(MODEL), "", (BW, BH), 0.6, 0.3, 5000)

    face_hits = {'tr': 0, 'tl': 0, 'br': 0, 'bl': 0, 'center': 0}
    with tempfile.TemporaryDirectory() as d:
        for i, t in enumerate(times):
            out = Path(d) / f"f{i}.png"
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(video_path),
                            '-frames:v', '1', '-vf', f'scale={BW}:{BH}', str(out)],
                           capture_output=True, timeout=15)
            if not out.exists():
                continue
            img = cv2.imread(str(out))
            if img is None:
                continue
            detector.setInputSize((img.shape[1], img.shape[0]))
            _, faces = detector.detect(img)
            if faces is not None:
                for face in faces:
                    fx, fy, fw, fh = face[:4]
                    cx = (fx + fw / 2) / BW
                    cy = (fy + fh / 2) / BH
                    if cy < 0.55:
                        if cx > 0.55:
                            face_hits['tr'] += 1
                        elif cx < 0.45:
                            face_hits['tl'] += 1
                        else:
                            face_hits['center'] += 1
                    else:
                        if cx > 0.55:
                            face_hits['br'] += 1
                        elif cx < 0.45:
                            face_hits['bl'] += 1

    best = max(face_hits, key=face_hits.get)
    if face_hits[best] >= 2:
        rects = {
            'tr': (0.58, 0.0, 0.42, 0.55),
            'tl': (0.0, 0.0, 0.42, 0.55),
            'br': (0.58, 0.45, 0.42, 0.55),
            'bl': (0.0, 0.45, 0.42, 0.55),
            'center': (0.25, 0.0, 0.50, 0.65),
        }
        return {'found': True, 'quadrant': best, 'rect': rects[best], 'hits': face_hits[best]}
    return {'found': False, 'quadrant': 'tr', 'rect': (0.58, 0.0, 0.42, 0.55)}


def _detect_fallback(video_path: Path) -> dict:
    from . import render
    quad = render.detect_cam_quadrant(Path(video_path), 0.0, 2.0)
    rects = {
        'tr': (0.58, 0.0, 0.42, 0.55),
        'tl': (0.0, 0.0, 0.42, 0.55),
        'br': (0.58, 0.45, 0.42, 0.55),
        'bl': (0.0, 0.45, 0.42, 0.55),
        'top': (0.25, 0.0, 0.50, 0.65),
    }
    return {'found': True, 'quadrant': quad, 'rect': rects.get(quad, (0.58, 0.0, 0.42, 0.55))}
