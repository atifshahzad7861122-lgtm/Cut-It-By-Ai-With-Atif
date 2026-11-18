import re
import unittest
from unittest.mock import MagicMock, patch
from studio import live

class TestLiveYouTubeChat(unittest.TestCase):
    def test_youtube_url_video_id_regex(self):
        urls = [
            ("https://www.youtube.com/watch?v=TzjbFaNs4p0", "TzjbFaNs4p0"),
            ("https://youtube.com/live/TzjbFaNs4p0?feature=share", "TzjbFaNs4p0"),
            ("https://youtu.be/TzjbFaNs4p0", "TzjbFaNs4p0"),
        ]
        for url, expected in urls:
            m = re.search(r"(?:v=|/live/|youtu\.be/)([A-Za-z0-9_-]{11})", url)
            self.assertIsNotNone(m, f"Failed regex on {url}")
            self.assertEqual(m.group(1), expected)

    def test_chat_spike_detection(self):
        job = {
            "id": "test-job-001",
            "source": {"url": "https://www.youtube.com/watch?v=TzjbFaNs4p0", "name": "Test"},
            "dir": ".",
            "clips": []
        }
        session = live.Session(job, {"live_per_hour": 4, "ai_every_min": 3, "min_score": 80, "must_clip_min": 0, "min_gap_min": 2})
        session.samples = 16000 * 120  # 120 seconds elapsed
        session.chat_total = 60         # 0.5 comments/sec average
        for s in range(50, 70):
            session.chat[s] = 4         # spike of 4 comments/sec during seconds 50-70

        # _chat_spike over window [55, 65] should be True (4.0 > max(3 * 0.5, 1.0))
        self.assertTrue(session._chat_spike(55, 65))
        # Window before the spike should be False
        self.assertFalse(session._chat_spike(10, 20))

    def test_watch_spikes_marks_chat_spike(self):
        job = {
            "id": "test-job-002",
            "source": {"url": "https://www.youtube.com/watch?v=TzjbFaNs4p0", "name": "Test"},
            "dir": ".",
            "clips": []
        }
        session = live.Session(job, {"live_per_hour": 4, "ai_every_min": 3, "min_score": 80, "must_clip_min": 0, "min_gap_min": 2})
        session.samples = 16000 * 100
        session.db = [-30.0] * 100  # constant quiet audio
        session.chat_on = True
        session.chat_total = 100
        # Background baseline: 1 comment per second
        for s in range(0, 92):
            session.chat[s] = 1
        # Recent 8 seconds: sudden burst of 6 comments per second
        for s in range(92, 100):
            session.chat[s] = 6

        session._watch_spikes()
        self.assertIsNotNone(session.spike, "Expected a spike to be marked on chat burst")
        self.assertIn("chat +", session.spike["why"])

    @patch("studio.live.threading.Thread")
    def test_start_launches_youtube_chat_thread(self, mock_thread):
        job = {
            "id": "test-job-003",
            "source": {"url": "https://www.youtube.com/watch?v=TzjbFaNs4p0", "name": "Test"},
            "dir": ".",
            "clips": []
        }
        session = live.Session(job, {})
        session.start()
        self.assertEqual(session.video_id, "TzjbFaNs4p0")
        # Should start _ingest, _analyze, and _chat_youtube
        self.assertEqual(mock_thread.call_count, 3)

if __name__ == "__main__":
    unittest.main()
