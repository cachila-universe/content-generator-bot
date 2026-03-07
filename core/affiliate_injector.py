"""Affiliate link injector using BeautifulSoup to add monetization links to content."""

from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# Any affiliate URL that still contains one of these placeholder strings is
# treated as "not yet configured" and will be silently skipped.
_PLACEHOLDER_TOKENS = {
    "YOUR_ID", "YOUR_TAG", "YOUR_AFF_ID", "YOUR_CJ_LINK",
    "YOUR_CHANNEL", "YOUR_REF", "YOUR_CODE", "YOUR_AFFILIATE",
}


def _is_configured(url: str) -> bool:
    """Return True only if the affiliate URL contains no known placeholder tokens."""
    url_upper = url.upper()
    return not any(tok in url_upper for tok in _PLACEHOLDER_TOKENS)


FTC_DISCLOSURE = (
    '<div class="ftc-disclosure" style="background:#fff3cd;border:1px solid #ffc107;'
    'padding:10px 14px;border-radius:4px;margin-bottom:20px;font-size:0.9em;">'
    '<strong>Disclosure:</strong> This post may contain affiliate links. '
    'If you click through and make a purchase, we may earn a commission at no extra cost to you. '
    'Thank you for supporting this site!'
    "</div>"
)


def inject_links(html_content: str, niche_config: dict, track_base_url: str = "") -> tuple:
    """
    Inject affiliate links into HTML content.

    Returns (modified_html, number_of_links_injected)
    """
    affiliate_programs = niche_config.get("affiliate_programs", [])
    if not affiliate_programs:
        return html_content, 0

    soup = BeautifulSoup(html_content, "lxml")
    links_injected = 0
    already_linked_keywords: set[str] = set()

    for program in affiliate_programs:
        aff_url = program.get("url", "")
        keywords = program.get("keywords", [])
        if not aff_url or not keywords:
            continue

        # Skip programs that still have a placeholder affiliate ID — injecting
        # broken links is worse than injecting no links at all.
        if not _is_configured(aff_url):
            logger.debug(
                "Skipping unconfigured affiliate program '%s' (placeholder URL detected)",
                program.get("name", "unknown"),
            )
            continue

        for keyword in keywords:
            if keyword.lower() in already_linked_keywords:
                continue

            # Find first text node containing the keyword (case-insensitive)
            injected = _inject_keyword(soup, keyword, aff_url, track_base_url)
            if injected:
                already_linked_keywords.add(keyword.lower())
                links_injected += 1

    # Add FTC disclosure at the top of the content
    disclosure_soup = BeautifulSoup(FTC_DISCLOSURE, "lxml")
    disclosure_div = disclosure_soup.find("div")

    body = soup.find("body")
    if body and body.contents and disclosure_div:
        body.insert(0, disclosure_div)
    elif disclosure_div:
        soup.insert(0, disclosure_div)

    return str(soup), links_injected


def _inject_keyword(soup: BeautifulSoup, keyword: str, aff_url: str, track_base_url: str) -> bool:
    """Find and replace the first occurrence of keyword with an affiliate link."""
    import re
    from bs4 import NavigableString

    keyword_lower = keyword.lower()
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)

    for element in soup.find_all(string=True):
        # Skip text nodes inside <a> tags or script/style/code
        if element.parent and element.parent.name in {"a", "script", "style", "code"}:
            continue

        text = str(element)
        if keyword_lower not in text.lower():
            continue

        match = pattern.search(text)
        if not match:
            continue

        # Build the href
        if track_base_url:
            href = f"{track_base_url}/track?url={quote_plus(aff_url)}"
        else:
            href = aff_url

        matched_text = match.group(0)
        before_text = text[: match.start()]
        after_text = text[match.end() :]

        # Build the link tag
        link_tag = soup.new_tag(
            "a", href=href, rel="nofollow sponsored", target="_blank"
        )
        link_tag.string = matched_text

        # Replace the text node with: before_text + <a>keyword</a> + after_text
        parent = element.parent
        if parent is None:
            continue

        # Insert new nodes in place of the original text node
        new_nodes = []
        if before_text:
            new_nodes.append(NavigableString(before_text))
        new_nodes.append(link_tag)
        if after_text:
            new_nodes.append(NavigableString(after_text))

        # Replace original element with the new nodes
        for i, node in enumerate(new_nodes):
            if i == 0:
                element.replace_with(node)
            else:
                new_nodes[i - 1].insert_after(node)

        return True

    return False
