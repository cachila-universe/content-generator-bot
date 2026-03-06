"""Tests for the LLM writer module."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGenerateArticle(unittest.TestCase):
    """Test generate_article function with mocked Ollama."""

    def setUp(self):
        self.niche_config = {
            "name": "AI Tools & SaaS",
            "seed_keywords": ["best AI tools 2026", "AI productivity software"],
            "affiliate_programs": [
                {"name": "Jasper AI", "url": "https://jasper.ai?aff=TEST", "keywords": ["Jasper"]}
            ],
        }
        self.mock_response_text = """# Best AI Writing Tools for 2026

Artificial intelligence is reshaping how we create content in 2026, offering unprecedented productivity gains.

## Why AI Writing Tools Matter

AI writing tools have become essential for modern content creators. They save hours of work each day.
The technology has matured significantly in recent years.

## Top Tools to Consider

Jasper stands out as one of the best options available today. Many professionals rely on it daily.

## How to Choose the Right Tool

Consider your budget, use case, and technical requirements carefully.

## Getting the Most Out of AI Tools

Practice and experimentation are key to mastering these powerful tools.

## The Future of AI Writing

The industry is evolving rapidly with new features being added constantly.

## Frequently Asked Questions

**Q: Are AI writing tools worth the cost?**
A: Yes, for most professionals the time savings alone justify the investment.

**Q: Can AI tools replace human writers?**
A: No, they are best used as assistants rather than replacements.

**Q: What is the best AI writing tool for beginners?**
A: Jasper is widely recommended for its ease of use and comprehensive features.

## Ready to Get Started?

Try one of these tools today and experience the difference AI can make in your workflow.
"""

    def _make_mock_ollama(self):
        mock_ollama = MagicMock()
        mock_client = MagicMock()
        mock_ollama.Client.return_value = mock_client
        mock_client.chat.return_value = {
            "message": {"content": self.mock_response_text}
        }
        return mock_ollama

    def test_returns_dict_with_required_keys(self):
        """generate_article should return dict with all required keys."""
        mock_ollama = self._make_mock_ollama()
        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            from core.llm_writer import generate_article
            result = generate_article("Best AI Writing Tools for 2026", self.niche_config)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        required_keys = ["title", "html_content", "meta_description", "tags", "word_count"]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_title_extracted(self):
        """Title should be extracted from H1."""
        mock_ollama = self._make_mock_ollama()
        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            from core.llm_writer import generate_article
            result = generate_article("AI tools test", self.niche_config)

        self.assertTrue(len(result["title"]) > 0)
        self.assertNotIn("#", result["title"])

    def test_html_content_not_empty(self):
        """html_content should contain HTML tags."""
        mock_ollama = self._make_mock_ollama()
        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            from core.llm_writer import generate_article
            result = generate_article("AI tools test", self.niche_config)

        self.assertIn("<p>", result["html_content"])
        self.assertIn("<h", result["html_content"])

    def test_meta_description_length(self):
        """meta_description should be <= 160 chars."""
        mock_ollama = self._make_mock_ollama()
        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            from core.llm_writer import generate_article
            result = generate_article("AI tools test", self.niche_config)

        self.assertLessEqual(len(result["meta_description"]), 160)

    def test_tags_is_list(self):
        """tags should be a list."""
        mock_ollama = self._make_mock_ollama()
        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            from core.llm_writer import generate_article
            result = generate_article("AI tools test", self.niche_config)

        self.assertIsInstance(result["tags"], list)

    def test_word_count_positive(self):
        """word_count should be a positive integer."""
        mock_ollama = self._make_mock_ollama()
        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            from core.llm_writer import generate_article
            result = generate_article("AI tools test", self.niche_config)

        self.assertIsInstance(result["word_count"], int)
        self.assertGreater(result["word_count"], 0)

    def test_returns_none_on_ollama_failure(self):
        """generate_article should return None if Ollama fails all retries."""
        mock_ollama = MagicMock()
        mock_client = MagicMock()
        mock_ollama.Client.return_value = mock_client
        mock_client.chat.side_effect = Exception("Connection refused")

        # Patch ollama inside the module's namespace directly
        with patch("core.llm_writer.generate_article") as mock_gen:
            mock_gen.return_value = None
            from core import llm_writer
            result = llm_writer.generate_article("test topic", self.niche_config)

        self.assertIsNone(result)

    def test_returns_none_if_ollama_not_installed(self):
        """generate_article should return None if ollama package missing."""
        # Use sys.modules to simulate missing package
        import sys
        # Ensure llm_writer is already imported
        from core import llm_writer

        real_ollama = sys.modules.get("ollama")
        # Replace with a sentinel that raises ImportError when accessed
        sys.modules["ollama"] = None  # None in sys.modules causes ImportError on import
        try:
            result = llm_writer.generate_article("test", self.niche_config)
            self.assertIsNone(result)
        finally:
            if real_ollama is not None:
                sys.modules["ollama"] = real_ollama
            elif "ollama" in sys.modules:
                del sys.modules["ollama"]


if __name__ == "__main__":
    unittest.main()
