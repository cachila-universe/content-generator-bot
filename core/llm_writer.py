"""
LLM-based article writer using Ollama with trend-intelligent style adaptation.

The writer queries the trend_intelligence module to:
  1. Pick the best article FORMAT for the topic (listicle, how-to, review, etc.)
  2. Craft style-specific prompts that match proven high-performing patterns
  3. Record which style was used so the intelligence system can learn
"""

import os
import re
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ── Style-specific prompt fragments ──────────────────────────────────────
_STYLE_PROMPTS = {
    "listicle": """
FORMAT: Listicle (Top-N list article)
- Structure the ENTIRE article as a numbered list of items
- Start the H1 title with a number (e.g., "10 Best...", "7 Must-Have...")
- Each list item gets its own ## H2 heading with the number and item name
- For each item: 2-3 sentences explaining why it's good, a key stat or price, and who it's best for
- Use bullet points within items for features/pros/cons
- Make the intro promise exactly how many items the reader will discover""",

    "how_to": """
FORMAT: How-To / Step-by-Step Guide
- Structure as a sequential tutorial with clear numbered steps
- Title should start with "How to..." or "The Complete Guide to..."
- Each step gets its own ## H2 heading: "Step 1: [Action]", "Step 2: [Action]"
- Include a "What You'll Need" or "Prerequisites" section early
- Add "Pro tip:" callouts within steps for expert advice
- End with a "Troubleshooting" or "Common Mistakes" section""",

    "comparison": """
FORMAT: Comparison / Head-to-Head
- Compare 2-3 products, tools, or approaches side-by-side
- Title should include "vs" or "Compared"
- Include a quick verdict in the intro (don't make readers scroll to find it)
- Use a markdown comparison table for specs/features
- Have dedicated sections for each option, then a "Winner for [use case]" section
- End with "Which One Should You Choose?" recommendation""",

    "review": """
FORMAT: In-Depth Review
- Title should include the product name and "Review"
- Open with your overall verdict (star rating, recommend or not)
- Include sections: First Impressions, Key Features, Performance, Pros & Cons, Value
- Use bullet-point lists for pros/cons
- Include specific metrics, prices, and real usage time
- End with "Is it worth it?" and clear recommendation""",

    "problem_solution": """
FORMAT: Problem-Solution Article
- Title should hint at a problem the reader has
- Open by acknowledging the reader's pain point — show you understand
- Clearly define the problem in the first section
- Provide 3-5 solutions, ranked from easiest to most effective
- Include real examples of people who solved this
- End with an action plan the reader can start TODAY""",

    "news_trending": """
FORMAT: Trending News Analysis
- Title should include the year and feel timely (e.g., "...in 2025")
- Open with the breaking development or trend
- Provide context: what changed, why it matters, who it affects
- Include expert quotes or data points
- Have a "What This Means For You" section
- End with predictions or next steps""",

    "beginner_guide": """
FORMAT: Beginner's Guide
- Title should include "for Beginners" or "Complete Guide"
- Start by reassuring the reader — no jargon, no assumptions
- Define key terms as you introduce them (bold + explanation)
- Use simple analogies to explain complex concepts
- Structure from basic → intermediate → "next steps"
- Include a glossary section or quick reference cheat sheet""",
}


def generate_article(topic: str, niche_config: dict, niche_id: str = "") -> dict | None:
    """
    Generate an SEO blog post using Ollama with intelligent style selection.

    The trend intelligence system recommends the best article format for the
    topic, then we craft a targeted prompt that matches proven patterns.

    Args:
        topic: The topic to write about
        niche_config: Niche configuration dict with name, keywords, etc.
        niche_id: The niche identifier (for trend intelligence lookup)

    Returns:
        dict with keys: title, html_content, meta_description, tags, word_count,
                        writing_style (style used)
        Returns None on failure.
    """
    try:
        import ollama
    except ImportError:
        logger.error("ollama package not installed. Run: pip install ollama")
        return None

    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
    niche_name = niche_config.get("name", "General")
    seed_keywords = niche_config.get("seed_keywords", [])

    # ── Trend intelligence: pick optimal writing style ────────────────────
    style_info = {"style_id": "listicle", "name": "Listicle"}
    try:
        from core.trend_intelligence import get_recommended_writing_style
        style_info = get_recommended_writing_style(niche_id or "", topic)
        logger.info("📝 Writing style chosen: %s (score: %s)", style_info["name"], style_info.get("effectiveness_score", "?"))
    except Exception as exc:
        logger.debug("Trend intelligence unavailable, using default style: %s", exc)

    style_id = style_info.get("style_id", "listicle")
    style_prompt = _STYLE_PROMPTS.get(style_id, _STYLE_PROMPTS["listicle"])

    prompt = f"""Write a complete, expert blog post about: "{topic}"

Niche: {niche_name}
Naturally include these keywords: {', '.join(seed_keywords[:5])}

{style_prompt}

General formatting rules (apply ON TOP of the format above):
- Start with a # H1 title (specific, compelling, optimized for clicks)
- Write an engaging 2-3 sentence introduction that hooks the reader immediately
- Write 5-7 sections — each with a descriptive ## H2 heading
- Mix up the format across sections. Use a variety of:
  • Bullet-point lists when comparing features, pros/cons, or listing recommendations
  • Numbered steps for how-to or process sections
  • Short punchy paragraphs (2-3 sentences max) mixed with lists
  • Bold key takeaways or product names at the start of list items
  • Quick comparison tables in markdown where relevant
- When recommending products or tools, ALWAYS use bullet points with this pattern:
  • **Product Name** — one-line description of why it's good, who it's for, and a standout feature
- End with a ## Frequently Asked Questions section containing 3 Q&As in this format:
  **Q: your question here**
  A: your answer here
- Finish with a short ## Conclusion paragraph (2-3 sentences, not a wall of text)

Writing style rules:
- Begin the article immediately — do NOT write any preamble like "Sure, here's an article"
- Every ## heading must be a real, descriptive title — never use placeholder words
- Be specific with product names, prices, specs, and real-world examples
- Vary your sentence length — mix short punchy sentences with longer explanatory ones
- Use conversational, friendly tone but back it up with authority and specifics
- Break up long explanations with subheadings (### H3) when a section gets long
- Include at least one "Pro tip:" or "Worth noting:" callout somewhere in the article
- Do NOT repeat the same sentence structure over and over
- Target 1000-1400 words"""

    for attempt in range(3):
        try:
            client = ollama.Client(host=host)
            response = client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response["message"]["content"]
            result = _parse_response(raw_text, niche_config)
            if result:
                result["writing_style"] = style_id
            return result
        except Exception as exc:
            logger.warning("Ollama attempt %d failed: %s", attempt + 1, exc)
            if attempt < 2:
                time.sleep(3)

    logger.error("All Ollama retries exhausted for topic: %s", topic)
    return None


def _parse_response(raw_text: str, niche_config: dict) -> dict:
    """Parse Ollama raw markdown/HTML response into structured article dict."""
    lines = raw_text.strip().splitlines()

    # Extract title from first H1
    title = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break

    if not title:
        # Fallback: use first non-empty line
        for line in lines:
            if line.strip():
                title = line.strip().lstrip("#").strip()
                break

    # Convert markdown to HTML
    html_content = _markdown_to_html(raw_text)

    # Extract meta description from first paragraph (~150 chars)
    meta_description = ""
    paragraphs = re.findall(r"<p>(.*?)</p>", html_content, re.DOTALL)
    if paragraphs:
        first_para = re.sub(r"<[^>]+>", "", paragraphs[0]).strip()
        meta_description = first_para[:150].rsplit(" ", 1)[0] + "…" if len(first_para) > 150 else first_para

    # Extract tags from niche keywords
    seed_keywords = niche_config.get("seed_keywords", [])
    tags = [kw.replace('"', "").strip() for kw in seed_keywords[:8]]

    # Word count from plain text
    plain_text = re.sub(r"<[^>]+>", " ", html_content)
    word_count = len(plain_text.split())

    return {
        "title": title,
        "html_content": html_content,
        "meta_description": meta_description,
        "tags": tags,
        "word_count": word_count,
    }


def _markdown_to_html(markdown: str) -> str:
    """Convert basic markdown to HTML."""
    lines = markdown.splitlines()
    html_lines = []
    in_paragraph = False
    in_faq = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            continue

        # H1
        if stripped.startswith("# "):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            html_lines.append(f"<h1>{stripped[2:].strip()}</h1>")
            continue

        # H2
        if stripped.startswith("## "):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            heading_text = stripped[3:].strip()
            # Strip any [placeholder] artifacts the LLM may have included literally
            heading_text = re.sub(r'^\[[^\]]*\]\s*', '', heading_text).strip()
            in_faq = "faq" in heading_text.lower() or "question" in heading_text.lower()
            html_lines.append(f"<h2>{heading_text}</h2>")
            continue

        # H3
        if stripped.startswith("### "):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            html_lines.append(f"<h3>{stripped[4:].strip()}</h3>")
            continue

        # Bold FAQ question
        if in_faq and stripped.startswith("**Q:"):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            q_text = stripped.strip("*").strip()
            html_lines.append(f'<p class="faq-question"><strong>{q_text}</strong></p>')
            continue

        # FAQ answer
        if in_faq and stripped.startswith("A:"):
            html_lines.append(f'<p class="faq-answer">{stripped[2:].strip()}</p>')
            continue

        # Bullet points
        if stripped.startswith("- ") or stripped.startswith("* "):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            # Collect list items
            item_text = _inline_markdown(stripped[2:].strip())
            html_lines.append(f"<li>{item_text}</li>")
            continue

        # Regular paragraph text
        inline = _inline_markdown(stripped)
        if not in_paragraph:
            html_lines.append(f"<p>{inline}")
            in_paragraph = True
        else:
            html_lines[-1] += " " + inline

    if in_paragraph:
        html_lines.append("</p>")

    # Wrap consecutive <li> items in <ul>
    result = "\n".join(html_lines)
    result = re.sub(r"(<li>.*?</li>\n?)+", lambda m: "<ul>\n" + m.group(0) + "</ul>\n", result, flags=re.DOTALL)
    return result


def _inline_markdown(text: str) -> str:
    """Convert inline markdown (bold, italic, code) to HTML."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text
