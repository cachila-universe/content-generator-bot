"""Tests for the trend finder module."""

import sys
import sqlite3
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analytics_tracker import init_db


class TestGetTrendingTopics(unittest.TestCase):
    """Test get_trending_topics with mocked pytrends."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = Path(self.tmp.name)
        init_db(self.db_path)

        self.niche_id = "ai_tools"
        self.niche_config = {
            "name": "AI Tools & SaaS",
            "seed_keywords": [
                "best AI tools 2026",
                "AI productivity software",
                "ChatGPT alternatives",
            ],
            "affiliate_programs": [],
        }

    def tearDown(self):
        try:
            self.db_path.unlink()
        except Exception:
            pass

    def _make_mock_pytrends(self, rising_data: list):
        """Build a mock TrendReq that returns given rising queries."""
        import pandas as pd

        mock_pytrends_module = MagicMock()
        mock_trend_req = MagicMock()
        mock_pytrends_module.request.TrendReq.return_value = mock_trend_req

        rising_df = pd.DataFrame(rising_data, columns=["query", "value"]) if rising_data else pd.DataFrame()
        top_df = pd.DataFrame()

        def mock_related(*args, **kwargs):
            seed = mock_trend_req.build_payload.call_args[0][0][0] if mock_trend_req.build_payload.call_args else ""
            return {seed: {"rising": rising_df, "top": top_df}}

        mock_trend_req.related_queries.side_effect = mock_related
        return mock_pytrends_module

    def test_returns_list(self):
        """Should always return a list."""
        from core.trend_finder import get_trending_topics

        result = get_trending_topics(self.niche_id, self.niche_config, self.db_path)
        self.assertIsInstance(result, list)

    def test_fallback_to_seed_keywords_when_pytrends_fails(self):
        """Should fall back to seed keywords when pytrends raises an exception."""
        mock_pytrends = MagicMock()
        mock_pytrends.request.TrendReq.side_effect = Exception("Rate limited")

        with patch.dict("sys.modules", {"pytrends": mock_pytrends, "pytrends.request": mock_pytrends.request}):
            from core import trend_finder
            import importlib
            importlib.reload(trend_finder)
            result = trend_finder.get_trending_topics(self.niche_id, self.niche_config, self.db_path)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_deduplicates_topics(self):
        """Result should not contain duplicate topics."""
        from core.trend_finder import get_trending_topics

        result = get_trending_topics(self.niche_id, self.niche_config, self.db_path)
        self.assertEqual(len(result), len(set(r.lower() for r in result)))

    def test_filters_existing_posts(self):
        """Topics already published should be filtered out."""
        # Insert an existing post with one of the seed keywords as title
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO posts (niche_id, niche_name, title, slug) VALUES (?, ?, ?, ?)",
            (self.niche_id, "AI Tools", "best AI tools 2026", "best-ai-tools-2026"),
        )
        conn.commit()
        conn.close()

        from core import trend_finder
        import importlib
        importlib.reload(trend_finder)

        result = trend_finder.get_trending_topics(self.niche_id, self.niche_config, self.db_path)
        titles_lower = [t.lower() for t in result]
        self.assertNotIn("best ai tools 2026", titles_lower)

    def test_returns_at_most_five_topics(self):
        """Should return at most 5 topics."""
        from core.trend_finder import get_trending_topics

        result = get_trending_topics(self.niche_id, self.niche_config, self.db_path)
        self.assertLessEqual(len(result), 5)

    def test_handles_missing_pytrends(self):
        """Should gracefully handle missing pytrends package."""
        original = sys.modules.pop("pytrends", None)
        original_req = sys.modules.pop("pytrends.request", None)
        try:
            from core import trend_finder
            import importlib
            importlib.reload(trend_finder)
            result = trend_finder.get_trending_topics(self.niche_id, self.niche_config, self.db_path)
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
        finally:
            if original is not None:
                sys.modules["pytrends"] = original
            if original_req is not None:
                sys.modules["pytrends.request"] = original_req


if __name__ == "__main__":
    unittest.main()
