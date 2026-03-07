"""LLM-based article writer using Ollama for local AI text generation."""

import os
import re
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_article(topic: str, niche_config: dict) -> dict | None:
    """
    Generate an SEO blog post using Ollama.

    Args:
        topic: The topic to write about
        niche_config: Niche configuration dict with name, keywords, etc.

    Returns:
        dict with keys: title, html_content, meta_description, tags, word_count
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

    prompt = f"""Write a complete, expert blog post about: "{topic}"

Niche: {niche_name}
Naturally include these keywords: {', '.join(seed_keywords[:5])}

Format the article in markdown:
- Start with a # H1 title (specific and compelling, not generic)
- Write an engaging 2-3 sentence introduction that hooks the reader immediately
- Write 5-7 sections — each with a descriptive ## H2 heading
- Mix up the format across sections. DO NOT write every section as long paragraphs. Use a variety of:
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
            return _parse_response(raw_text, niche_config)
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
