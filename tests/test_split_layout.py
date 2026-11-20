"""Unit tests for Split layout (Creator on top, Gameplay on bottom)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, ".")
from studio import config, render


class TestSplitLayout(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pc-split-test-"))

    def test_layouts_registered(self):
        self.assertIn("split", render.LAYOUTS)
        self.assertIn("split_tr", render.LAYOUTS)
        self.assertIn("split_tl", render.LAYOUTS)
        self.assertIn("split_br", render.LAYOUTS)
        self.assertIn("split_bl", render.LAYOUTS)
        self.assertIn("split_top", render.LAYOUTS)

    def test_geometry_split(self):
        layout, fg_h, hook_y, cap_y = render.geometry(1920, 1080, "split")
        self.assertEqual(layout, "split")
        self.assertEqual(fg_h, render.H)
        self.assertEqual(hook_y, 200)
        self.assertEqual(cap_y, 880)

        # Test sub-layouts
        for sub in ("split_tr", "split_tl", "split_br", "split_bl", "split_top"):
            l, h, hy, cy = render.geometry(1280, 720, sub)
            self.assertEqual(l, sub)
            self.assertEqual(h, render.H)
            self.assertEqual((hy, cy), (200, 880))

    def test_filter_generation_split(self):
        filt = render._filter("split", 1920, cam_pos="tr")
        self.assertIn("vstack=inputs=2", filt)
        self.assertIn("drawbox=x=0:y=858", filt)
        self.assertIn("scale=1080:860", filt)
        self.assertIn("scale=1080:1060", filt)
        self.assertIn("crop=1080:860", filt)
        self.assertIn("crop=1080:1060", filt)

        # Test Top-Left quadrant
        filt_tl = render._filter("split_tl", 1920)
        self.assertIn("x=0:y=0", filt_tl)

        # Test Bottom-Right quadrant
        filt_br = render._filter("split_br", 1920)
        self.assertIn("x=iw-ow:y=ih-oh", filt_br)

    def test_render_clip_split_execution(self):
        # 1. Generate 2-second 16:9 source video with a face-like box in top right
        src = self.tmp / "gaming_stream.mp4"
        cmd = [
            "ffmpeg", "-y", "-v", "error", "-f", "lavfi",
            "-i", "testsrc=size=1280x720:rate=30,drawbox=x=850:y=30:w=350:h=280:color=#D29678@1:t=fill",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
            "-t", "2", "-c:v", "libx264", "-c:a", "aac", str(src)
        ]
        subprocess.run(cmd, check=True)

        # 2. Render split clip
        out_dir = self.tmp / "output_clips"
        clip_data = {
            "start": 0.0,
            "end": 1.5,
            "hook": "SPEED IN GTA 6",
            "style": "bounce",
            "layout": "split",
            "highlight_words": ["GTA", "6"],
            "watermark": True
        }
        words = [
            {"w": "Speed", "s": 0.1, "e": 0.5},
            {"w": "in", "s": 0.5, "e": 0.8},
            {"w": "GTA", "s": 0.8, "e": 1.1},
            {"w": "6", "s": 1.1, "e": 1.4}
        ]

        res = render.render_clip(src, out_dir, "clip_speed", clip_data, words, 1280, 720)
        self.assertEqual(res["file"], "clip_speed.mp4")
        self.assertEqual(res["layout"], "split")

        mp4_path = out_dir / "clip_speed.mp4"
        jpg_path = out_dir / "clip_speed.jpg"
        ass_path = out_dir / "clip_speed.ass"

        self.assertTrue(mp4_path.is_file())
        self.assertTrue(jpg_path.is_file())
        self.assertTrue(ass_path.is_file())
        self.assertGreater(mp4_path.stat().st_size, 1000)

        # 3. Verify probe output is 1080x1920 (vertical 9:16)
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", str(mp4_path)],
            capture_output=True, text=True, check=True
        )
        self.assertEqual(probe.stdout.strip(), "1080x1920")

        # 4. Verify ASS subtitle file has Hook at y~200 and captions at y~880
        ass_content = ass_path.read_text(encoding="utf-8")
        self.assertIn("SPEED IN GTA 6", ass_content)
        self.assertIn("\\pos(540,", ass_content)
        self.assertIn("888)", ass_content)


if __name__ == "__main__":
    unittest.main()
