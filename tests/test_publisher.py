"""Tests for the static site publisher module."""

import sys
import unittest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analytics_tracker import init_db


class TestPublisher(unittest.TestCase):
    """Test the publish function with a temp directory."""

    def setUp(self):
        # Create a temporary database
        self.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = Path(self.tmp_db.name)
        init_db(self.db_path)

        self.niche_id = "ai_tools"
        self.niche_name = "AI Tools & SaaS"

        self.article = {
            "title": "Best AI Tools for Productivity in 2025",
            "html_content": """
<div class="ftc-disclosure">Disclosure: This post may contain affiliate links.</div>
<h1>Best AI Tools for Productivity in 2025</h1>
<p>Discover the top AI tools that will boost your productivity this year.</p>
<h2>Why AI Tools Matter</h2>
<p>AI tools save time and increase efficiency for modern professionals.</p>
<h2>Frequently Asked Questions</h2>
<p class="faq-question"><strong>Q: What is the best AI tool?</strong></p>
<p class="faq-answer">A: It depends on your use case, but Jasper is highly rated.</p>
<h2>Ready to Start?</h2>
<p>Try these tools today and experience the difference.</p>
""",
            "meta_description": "Discover the best AI tools for productivity in 2025.",
            "meta_html": "<title>Best AI Tools | TechLife Insights</title>",
            "schema_markup": "",
            "tags": ["AI tools", "productivity", "ChatGPT"],
            "slug": "best-ai-tools-productivity-2025",
            "canonical_url": "http://localhost:8080/ai_tools/best-ai-tools-productivity-2025.html",
            "published_at": "2025-01-15T10:00:00Z",
            "word_count": 120,
            "affiliate_links_count": 2,
        }

        self.settings = {
            "site": {"title": "TechLife Insights", "tagline": "Smart Guides"},
            "analytics": {"avg_commission_value": 25.0, "estimated_ctr": 0.02},
            "site_url": "http://localhost:8080",
        }

    def tearDown(self):
        try:
            self.db_path.unlink()
        except Exception:
            pass

    def test_html_file_created(self):
        """publish() should create an HTML file in site/output/{niche_id}/."""
        from core.publisher import publish, _OUTPUT_DIR

        url_path = publish(self.article, self.niche_id, self.niche_name, self.settings, self.db_path)

        expected_file = _OUTPUT_DIR / self.niche_id / f"{self.article['slug']}.html"
        self.assertTrue(expected_file.exists(), f"Expected file not found: {expected_file}")

    def test_html_contains_article_title(self):
        """Published HTML should contain the article title."""
        from core.publisher import publish, _OUTPUT_DIR

        publish(self.article, self.niche_id, self.niche_name, self.settings, self.db_path)

        html_file = _OUTPUT_DIR / self.niche_id / f"{self.article['slug']}.html"
        if html_file.exists():
            content = html_file.read_text(encoding="utf-8")
            self.assertIn("Best AI Tools for Productivity in 2025", content)

    def test_html_contains_ftc_disclosure(self):
        """Published HTML should contain FTC disclosure."""
        from core.publisher import publish, _OUTPUT_DIR

        publish(self.article, self.niche_id, self.niche_name, self.settings, self.db_path)

        html_file = _OUTPUT_DIR / self.niche_id / f"{self.article['slug']}.html"
        if html_file.exists():
            content = html_file.read_text(encoding="utf-8")
            # Should contain disclosure text somewhere
            self.assertTrue(
                "Disclosure" in content or "disclosure" in content or "affiliate" in content.lower(),
                "FTC disclosure text not found in published HTML"
            )

    def test_returns_url_path(self):
        """publish() should return a non-empty URL path string."""
        from core.publisher import publish

        url_path = publish(self.article, self.niche_id, self.niche_name, self.settings, self.db_path)

        self.assertIsInstance(url_path, str)
        self.assertTrue(url_path.startswith("/") or url_path == "")

    def test_post_saved_to_database(self):
        """publish() should save the post to the SQLite database."""
        from core.publisher import publish
        from core.analytics_tracker import get_all_posts

        publish(self.article, self.niche_id, self.niche_name, self.settings, self.db_path)

        posts = get_all_posts(self.db_path)
        slugs = [p["slug"] for p in posts]
        self.assertIn(self.article["slug"], slugs)

    def test_index_html_rebuilt(self):
        """publish() should rebuild site/output/index.html."""
        from core.publisher import publish, _OUTPUT_DIR

        publish(self.article, self.niche_id, self.niche_name, self.settings, self.db_path)

        index_file = _OUTPUT_DIR / "index.html"
        self.assertTrue(index_file.exists(), "index.html should be rebuilt after publishing")

    def test_multiple_publishes_no_duplicate_slugs(self):
        """Publishing the same article twice should not create duplicate DB entries."""
        from core.publisher import publish
        from core.analytics_tracker import get_all_posts

        publish(self.article, self.niche_id, self.niche_name, self.settings, self.db_path)
        publish(self.article, self.niche_id, self.niche_name, self.settings, self.db_path)

        posts = get_all_posts(self.db_path)
        matching = [p for p in posts if p["slug"] == self.article["slug"]]
        # Should be at most 1 due to UNIQUE constraint on slug
        self.assertLessEqual(len(matching), 1)


if __name__ == "__main__":
    unittest.main()
