"""Test Multi-Stream Studio: watch, record, and auto-clip 5 to 6 live streams concurrently."""
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-mstream-")
os.environ.update(DATABASE_URL="", PEAKCUT_ACCOUNTS="0", PEAKCUT_PUBLIC_URL="http://127.0.0.1:8765",
                  PEAKCUT_MAX_LIVE="20")
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from studio import auth, config, creators, ctx, db, jobs, live, load, server

db.init()
BASE = "http://127.0.0.1:8765"
ORIGIN = {"Origin": BASE}


class TestMultiStreamStudio(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(server.app, base_url=BASE, follow_redirects=False)
        # Mock Session.start to not spawn real ffmpeg processes during tests
        self._orig_start = live.Session.start
        live.Session.start = lambda s: live.SESSIONS.__setitem__(s.job["id"], s)
        live.SESSIONS.clear()

    def tearDown(self):
        live.Session.start = self._orig_start
        live.SESSIONS.clear()

    def test_active_live_streams_endpoint_empty(self):
        r = self.client.get("/api/live/active")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["streams"], [])
        self.assertEqual(data["max_allowed"], 6)

    def test_start_stream_url_and_multi_stream_concurrency(self):
        # 1. Start 6 streams concurrently
        stream_urls = [
            f"https://www.twitch.tv/pro_streamer_{i}" for i in range(1, 7)
        ]

        started = []
        with ctx.as_user(auth.local_user().id):
            for u in stream_urls:
                j = live.start_stream_url(u)
                started.append(j)

            self.assertEqual(len(started), 6)
            self.assertEqual(len(live.active_mine()), 6)

        # 2. Check /api/live/active reports all 6 streams
        r = self.client.get("/api/live/active")
        self.assertEqual(r.status_code, 200)
        active_data = r.json()
        self.assertEqual(active_data["count"], 6)
        self.assertEqual(len(active_data["streams"]), 6)

        # Verify platform and embed resolution
        platforms = [s["platform"] for s in active_data["streams"]]
        self.assertTrue(all(p == "twitch" for p in platforms))

        # 3. Verify attempting a 7th stream is refused
        r_7th = self.client.post("/api/live/watch", json={"url": "https://www.twitch.tv/streamer_extra_7"}, headers=ORIGIN)
        self.assertEqual(r_7th.status_code, 400)
        self.assertIn("at most 6 streams", r_7th.text)

        # 4. Stop all streams
        r_stop = self.client.post("/api/live/stop-all", headers=ORIGIN)
        self.assertEqual(r_stop.status_code, 200)
        self.assertEqual(r_stop.json()["stopped"], 6)

        # Check /api/live/active is now 0
        r_after = self.client.get("/api/live/active")
        self.assertEqual(r_after.json()["count"], 0)

    def test_watch_endpoint_batch_submission(self):
        # Test submitting a batch of 3 URLs in one call
        batch = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.twitch.tv/esl_csgo",
            "https://kick.com/xqc"
        ]
        r = self.client.post("/api/live/watch", json={"urls": batch}, headers=ORIGIN)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["count"], 3)
        self.assertEqual(len(data["started"]), 3)

        # Check active streams endpoint has YouTube, Twitch, and Kick
        r_active = self.client.get("/api/live/active")
        plats = {s["platform"] for s in r_active.json()["streams"]}
        self.assertIn("youtube", plats)
        self.assertIn("twitch", plats)
        self.assertIn("kick", plats)

        # Clean up
        self.client.post("/api/live/stop-all", headers=ORIGIN)

    def test_multistream_autopost_preferences_and_post_all(self):
        # 1. Check GET /api/live/autopost
        r_get = self.client.get("/api/live/autopost")
        self.assertEqual(r_get.status_code, 200)
        self.assertIn("autopost", r_get.json())

        # 2. Update preferences via POST /api/live/autopost
        r_set = self.client.post("/api/live/autopost", json={
            "autopost": True,
            "accounts": ["acc_yt_01", "acc_ig_01"],
            "min_score": 70
        }, headers=ORIGIN)
        self.assertEqual(r_set.status_code, 200)
        self.assertTrue(r_set.json()["autopost"])
        self.assertEqual(r_set.json()["accounts"], ["acc_yt_01", "acc_ig_01"])

        # 3. Start a stream and verify it inherits autopost
        r_start = self.client.post("/api/live/watch", json={
            "url": "https://www.twitch.tv/ninja_hype"
        }, headers=ORIGIN)
        self.assertEqual(r_start.status_code, 200)

        r_active = self.client.get("/api/live/active")
        self.assertEqual(r_active.status_code, 200)
        streams = r_active.json()["streams"]
        self.assertEqual(len(streams), 1)
        self.assertTrue(streams[0]["autopost"])
        self.assertIn("acc_yt_01", streams[0]["accounts"])

        # 4. Attach a completed clip to the live job
        jid = streams[0]["job_id"]
        with ctx.as_user(auth.local_user().id):
            job = jobs.get(jid)
            self.assertIsNotNone(job)
            clip = {
                "id": "clip001",
                "title": "Insane Headshot",
                "hook": "UNBELIEVABLE",
                "score": 85,
                "status": "done",
                "file": "clip001.mp4"
            }
            job["clips"].append(clip)
            jobs.save(job)

        # 5. Test POST /api/live/post-all with mock posting.enqueue
        with patch("studio.posting.enqueue") as mock_enqueue:
            mock_enqueue.return_value = [{"id": "p001"}]
            r_post = self.client.post("/api/live/post-all", json={
                "accounts": ["acc_yt_01"]
            }, headers=ORIGIN)
            self.assertEqual(r_post.status_code, 200)
            data = r_post.json()
            self.assertTrue(data["ok"])
            self.assertEqual(data["queued"], 1)
            self.assertEqual(data["clips_count"], 1)
            mock_enqueue.assert_called_once()

        # Clean up
        self.client.post("/api/live/stop-all", headers=ORIGIN)

    def test_gaming_hype_and_triggers(self):
        from studio import excite
        # Verify English, Hindi, and Hinglish gaming hype matches
        self.assertTrue(excite.match_hype("what a headshot bhai")[0])
        self.assertTrue(excite.match_hype("bhai kya mara")[0])
        self.assertTrue(excite.match_hype("op clutch")[0])
        self.assertTrue(excite.match_hype("are baap re")[0])
        self.assertTrue(excite.match_hype("holy shit what a play")[0])
        self.assertFalse(excite.match_hype("just eating some breakfast")[0])


if __name__ == "__main__":
    unittest.main()
