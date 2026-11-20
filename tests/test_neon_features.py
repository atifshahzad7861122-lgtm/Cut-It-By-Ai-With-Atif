"""Unit tests for combined NeonClipping features: 11 layouts, multi-aspect ratios,
circle cam, excitement scoring, curation profiles, styling, and subtitle import/export."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-neon-test-")
os.environ.update(DATABASE_URL="", PEAKCUT_ACCOUNTS="0", PEAKCUT_PUBLIC_URL="http://127.0.0.1:8765")
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from studio import auth, brands, config, ctx, curation, db, excite, facecam_detect, jobs, layouts, render, server, styling, subtitles

db.init()
BASE = "http://127.0.0.1:8765"
ORIGIN = {"Origin": BASE}


class TestNeonCombinedFeatures(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(server.app, base_url=BASE, follow_redirects=False)

    def test_layouts_catalog_and_geometry(self):
        # 1. Verify 11 layouts catalog
        self.assertEqual(len(layouts.CATALOG), 11)
        catalog_ids = [k for k, _, _ in layouts.CATALOG]
        for expected in ("stack", "bottom", "blur", "fill", "game", "pip_tl", "pip_tr", "pip_bl", "pip_br", "circle", "side"):
            self.assertIn(expected, catalog_ids)

        # 2. Verify output settings for all aspect ratios
        for asp, expected_res in (("vertical", (1080, 1920)), ("square", (1080, 1080)), ("portrait", (1080, 1350)), ("landscape", (1920, 1080)), ("threefour", (1080, 1440))):
            w, h, _ = layouts.output_settings({"aspect": asp, "resolution": 1080})
            self.assertEqual((w, h), expected_res)

        # 3. Verify render graph generation for circle camera
        cg = layouts.render_graph("circle", top=0.38, width=1080, height=1920)
        self.assertIn("geq=", cg)
        self.assertIn("pow(min(W,H)/2,2)", cg)

        # 4. Verify render graph generation for stack
        sg = layouts.render_graph("stack", top=0.40, width=1080, height=1920)
        self.assertIn("drawbox=", sg)

    def test_excite_scoring(self):
        # Hindi & English gamer exclamations
        self.assertGreater(excite.word_weight("arre"), 0.5)
        self.assertGreater(excite.word_weight("bhaago"), 1.5)
        self.assertGreater(excite.word_weight("dhamaka"), 1.5)
        self.assertGreater(excite.word_weight("omg"), 2.0)
        self.assertGreater(excite.word_weight("insane"), 1.5)

        words = [
            {"text": "oh", "start": 1.0, "end": 1.4},
            {"text": "my", "start": 1.4, "end": 1.7},
            {"text": "god", "start": 1.7, "end": 2.2},
            {"text": "bhaago", "start": 3.0, "end": 3.6},
            {"text": "police", "start": 4.0, "end": 4.5},
        ]
        sig = excite.seconds_signal(words, 10.0)
        self.assertEqual(len(sig), 10)
        self.assertGreater(sig[1], 0.0)

        score = excite.window_score(words, 5.0)
        self.assertGreater(score, 0.2)

    def test_curation_profiles_and_hooks(self):
        # Focus settings
        brief, inc, exc = curation.focus_settings({
            "focus_brief": "epic clutch win with sniper",
            "include_phrases": ["clutch", "headshot"],
            "exclude_phrases": ["intro", "sponsor"]
        })
        self.assertEqual(brief, "epic clutch win with sniper")
        self.assertIn("clutch", inc)
        self.assertIn("sponsor", exc)

        # Filter check
        self.assertTrue(curation.passes_filters("that was an epic clutch shot", includes=tuple(inc), excludes=tuple(exc)))
        self.assertFalse(curation.passes_filters("check our sponsor today", includes=tuple(inc), excludes=tuple(exc)))

        # Hook extraction
        text = "we were walking down the street. but actually the police arrived and car had no keys!"
        hook = curation.extract_hook(text)
        self.assertTrue(len(hook) > 0)
        self.assertTrue(curation.hook_supported("the police arrived and car had no keys", text))

        # Filler detection
        self.assertTrue(curation.filler("welcome back everyone, give me a minute to set up"))

    def test_styling_and_watermark(self):
        plan = styling.build_style_plan({"bg_mode": "gradient", "watermark_pos": "tl", "padding": 30, "radius": 20})
        self.assertEqual(plan["bg_mode"], "gradient")
        self.assertEqual(plan["watermark_pos"], "tl")
        self.assertEqual(plan["padding"], 30)

        wx, wy = styling.watermark_coordinates("tl", 96, 1080, 1920)
        self.assertEqual((wx, wy), (48, 48))

        wx2, wy2 = styling.watermark_coordinates("br", 96, 1080, 1920)
        self.assertEqual((wx2, wy2), (1080 - 96 - 48, 1920 - 96 - 48))

    def test_subtitles_parsing_and_writing(self):
        srt_raw = """1
00:00:01,000 --> 00:00:03,500
Speed said good morning in GTA

2
00:00:03,600 --> 00:00:06,000
Right in front of the cafe
"""
        cues = subtitles.parse_track(srt_raw)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]["start"], 1.0)
        self.assertEqual(cues[0]["end"], 3.5)

        # Write to WebVTT
        vtt = subtitles.write_track(cues, format="vtt")
        self.assertTrue(vtt.startswith("WEBVTT"))
        self.assertIn("00:00:01.000 --> 00:00:03.500", vtt)

        # Spread cues to words
        words = subtitles.cues_to_words(cues)
        self.assertGreater(len(words), 5)
        self.assertEqual(words[0]["w"], "Speed")
        self.assertGreater(words[1]["s"], words[0]["s"])

    def test_api_layouts_and_brands(self):
        # 1. GET /api/layouts
        r_lay = self.client.get("/api/layouts")
        self.assertEqual(r_lay.status_code, 200)
        data = r_lay.json()
        self.assertIn("catalog", data)
        self.assertIn("aspects", data)
        self.assertEqual(len(data["catalog"]), 11)

        # 2. POST /api/brands
        b_payload = {
            "name": "Neon Streamer Brand",
            "settings": {
                "caption_font": "Anton",
                "caption_size": 130,
                "caption_color": "#FFFFFF",
                "caption_active": "#FF8B33",
                "caption_outline": "#000000",
                "caption_max_words": 3
            }
        }
        r_save = self.client.post("/api/brands", json=b_payload, headers=ORIGIN)
        self.assertEqual(r_save.status_code, 200)

        # 3. GET /api/brands
        r_list = self.client.get("/api/brands")
        self.assertEqual(r_list.status_code, 200)
        b_data = r_list.json()
        self.assertIn("Neon Streamer Brand", b_data["profiles"])


if __name__ == "__main__":
    unittest.main()
