"""
Charles Schwab Market Commentary — https://www.schwab.com/learn/market-commentary
Returns articles published within the last 24 hours.
The page is Next.js SSR; article data lives in script tags as JSON-LD or
in the rendered HTML. Falls back to BeautifulSoup link extraction.
"""
from datetime import datetime, timedelta, timezone
import json
import re
import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.schwab.com/learn/market-commentary"
CUTOFF_HOURS = 24

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}


def _parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s.rstrip("Z"), fmt.rstrip("%z"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def fetch():
    resp = requests.get(PAGE_URL, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    html = resp.text

    cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)
    items = []

    # Strategy 1: JSON-LD structured data
    for script_content in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.DOTALL
    ):
        try:
            blob = json.loads(script_content)
            # May be a list or single object
            entries = blob if isinstance(blob, list) else [blob]
            for entry in entries:
                # ItemList pattern
                if entry.get("@type") == "ItemList":
                    for el in entry.get("itemListElement", []):
                        item = el.get("item", el)
                        title = item.get("name") or item.get("headline") or ""
                        url   = item.get("url") or ""
                        date  = _parse_date(item.get("datePublished"))
                        if title and url:
                            if date and date < cutoff:
                                continue
                            items.append({
                                "title": title.strip(),
                                "url": url,
                                "date": date.isoformat() if date else None,
                                "summary": (item.get("description") or "").strip() or None,
                            })
                # Article / NewsArticle pattern
                elif entry.get("@type") in ("Article", "NewsArticle"):
                    title = entry.get("headline") or entry.get("name") or ""
                    url   = entry.get("url") or entry.get("mainEntityOfPage", {}).get("@id") or ""
                    date  = _parse_date(entry.get("datePublished"))
                    desc  = entry.get("description") or ""
                    if title and url:
                        if date and date < cutoff:
                            continue
                        items.append({
                            "title": title.strip(),
                            "url": url,
                            "date": date.isoformat() if date else None,
                            "summary": desc.strip() or None,
                        })
        except (json.JSONDecodeError, AttributeError):
            continue

    if items:
        return items

    # Strategy 2: BeautifulSoup fallback — find article cards
    soup = BeautifulSoup(html, "html.parser")

    # Common article card selectors on schwab.com
    selectors = [
        "article", "[class*='article']", "[class*='card']",
        "[class*='story']", "[class*='insight']"
    ]
    seen_urls = set()

    for selector in selectors:
        for card in soup.select(selector):
            a_tag = card.find("a", href=True)
            if not a_tag:
                continue
            href = a_tag["href"]
            if not href.startswith("/learn/story"):
                continue
            url = f"https://www.schwab.com{href}"
            if url in seen_urls:
                continue
            seen_urls.add(url)

            heading = card.find(["h2", "h3", "h4"])
            title   = heading.get_text(strip=True) if heading else a_tag.get_text(strip=True)

            # Look for date metadata
            time_tag = card.find("time")
            date_str = time_tag.get("datetime") if time_tag else None
            date     = _parse_date(date_str)
            if date and date < cutoff:
                continue

            p_tag   = card.find("p")
            summary = p_tag.get_text(strip=True) if p_tag else None

            if title:
                items.append({
                    "title": title,
                    "url": url,
                    "date": date.isoformat() if date else None,
                    "summary": summary,
                })

    return items
