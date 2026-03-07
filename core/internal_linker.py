"""Internal linking engine — adds cross-references between published articles."""

import re
import logging
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

logger = logging.getLogger(__name__)

# Maximum internal links to inject per article
MAX_LINKS_PER_ARTICLE = 3


def inject_internal_links(html_content: str, current_slug: str, all_posts: list, site_url: str) -> str:
    """
    Scan article HTML and add internal links to other published articles
    when their title keywords appear naturally in the text.

    Args:
        html_content: The article HTML body.
        current_slug: Slug of the current article (to avoid self-linking).
        all_posts: List of all published post dicts from the database.
        site_url: Base site URL.

    Returns:
        Modified HTML with internal links injected.
    """
    if not all_posts or len(all_posts) < 2:
        return html_content

    # Build a lookup of linkable phrases from other articles
    link_targets = []
    for post in all_posts:
        slug = post.get("slug", "")
        if not slug or slug == current_slug:
            continue

        title = post.get("title", "")
        url = post.get("url", "")
        if not title or not url:
            continue

        # Extract meaningful phrases from the title (3+ word chunks and full title)
        phrases = _extract_link_phrases(title)
        for phrase in phrases:
            link_targets.append({
                "phrase": phrase,
                "url": url,
                "title": title,
            })

    if not link_targets:
        return html_content

    # Sort by phrase length (longer phrases first = more specific matches)
    link_targets.sort(key=lambda x: len(x["phrase"]), reverse=True)

    soup = BeautifulSoup(html_content, "lxml")
    links_added = 0
    linked_urls = set()

    for target in link_targets:
        if links_added >= MAX_LINKS_PER_ARTICLE:
            break

        # Don't link to the same article twice
        if target["url"] in linked_urls:
            continue

        phrase = target["phrase"]
        if len(phrase) < 8:  # Skip very short phrases
            continue

        injected = _inject_link(soup, phrase, target["url"], target["title"])
        if injected:
            linked_urls.add(target["url"])
            links_added += 1
            logger.debug("Internal link: '%s' → %s", phrase, target["url"])

    if links_added > 0:
        logger.info("Injected %d internal links into article", links_added)

    return str(soup)


def _extract_link_phrases(title: str) -> list:
    """Extract linkable keyword phrases from an article title."""
    # Clean the title
    clean = re.sub(r"[^a-zA-Z0-9\s\-]", "", title).strip()
    words = clean.split()

    phrases = []

    # Full title (minus common prefixes like "Top 10", "Best", "How to")
    phrases.append(clean)

    # Remove leading numbers and filler words
    stripped = re.sub(
        r"^(top\s+\d+|best|\d+\s+best|how\s+to|the|a|an)\s+",
        "",
        clean,
        flags=re.IGNORECASE,
    ).strip()
    if stripped and stripped != clean:
        phrases.append(stripped)

    # 3-word and 4-word chunks (if title is long enough)
    if len(words) >= 5:
        for i in range(len(words) - 2):
            chunk = " ".join(words[i : i + 3])
            if len(chunk) >= 10:
                phrases.append(chunk)

    return phrases


def _inject_link(soup: BeautifulSoup, phrase: str, url: str, title: str) -> bool:
    """Find the first occurrence of phrase in text and wrap it with an internal link."""
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)

    for element in soup.find_all(string=True):
        # Skip text inside existing links, scripts, styles, headings
        if element.parent and element.parent.name in {"a", "script", "style", "code", "h1", "h2", "h3"}:
            continue

        text = str(element)
        if phrase.lower() not in text.lower():
            continue

        match = pattern.search(text)
        if not match:
            continue

        matched_text = match.group(0)
        before = text[: match.start()]
        after = text[match.end() :]

        link_tag = soup.new_tag("a", href=url, title=title)
        link_tag.string = matched_text

        parent = element.parent
        if parent is None:
            continue

        new_nodes = []
        if before:
            new_nodes.append(NavigableString(before))
        new_nodes.append(link_tag)
        if after:
            new_nodes.append(NavigableString(after))

        for i, node in enumerate(new_nodes):
            if i == 0:
                element.replace_with(node)
            else:
                new_nodes[i - 1].insert_after(node)

        return True

    return False
