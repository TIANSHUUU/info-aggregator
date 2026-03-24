"""
Charles Schwab Market Commentary
Fetches article listing, then visits each article page to get
publication date and English description, translating it to Chinese.
Only returns articles published within the last 24 hours.
"""
import re
import json
import time
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup

LIST_URL = "https://www.schwab.com/learn/market-commentary"
BASE_URL  = "https://www.schwab.com"
CUTOFF_HOURS = 24

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
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


def _fetch_article_meta(url, session):
    """Fetch date and English description from individual article page."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if not resp.ok:
            return None, None
        html = resp.text

        date_iso = None
        desc_en  = None

        # Try JSON-LD
        for block in re.findall(
            r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
            html, re.DOTALL
        ):
            try:
                d = json.loads(block)
                entries = d if isinstance(d, list) else [d]
                for e in entries:
                    if not date_iso and e.get("datePublished"):
                        date_iso = e["datePublished"]
                    if not desc_en and e.get("description"):
                        desc_en = e["description"]
            except Exception:
                pass

        # Fallback: meta tags
        if not date_iso:
            m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
            if m:
                date_iso = m.group(1)
        if not desc_en:
            m = re.search(r'<meta\s+name="description"\s+content="([^"]{20,})"', html)
            if m:
                desc_en = m.group(1).replace("&#x27;", "'")

        return date_iso, desc_en
    except Exception:
        return None, None


def _translate_to_zh(text, session):
    """Translate English text to Chinese using Google Translate (unofficial, free)."""
    if not text:
        return None
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "zh-CN",
            "dt": "t",
            "q": text[:500],
        }
        resp = session.get(url, params=params, timeout=10)
        data = resp.json()
        translated = "".join(part[0] for part in data[0] if part[0])
        return translated.strip() or None
    except Exception:
        return None


def fetch():
    cutoff  = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)
    session = requests.Session()

    # Step 1: get article list
    resp = session.get(LIST_URL, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    seen_urls  = set()
    candidates = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("/learn/story"):
            continue
        url   = BASE_URL + href
        if url in seen_urls:
            continue
        seen_urls.add(url)

        heading = a.find(["h1","h2","h3","h4"])
        title   = heading.get_text(strip=True) if heading else a.get_text(strip=True)
        if len(title) < 8:
            continue
        candidates.append({"title": title, "url": url})

    if not candidates:
        return []

    # Step 2: fetch dates + descriptions from article pages (top 8 only)
    items = []
    for c in candidates[:8]:
        date_str, desc_en = _fetch_article_meta(c["url"], session)
        pub_dt = _parse_date(date_str)

        if pub_dt and pub_dt < cutoff:
            continue  # older than 24h — skip

        # If no date found at all, include it (can't filter)
        desc_zh = _translate_to_zh(desc_en, session) if desc_en else None

        items.append({
            "title":   c["title"],
            "url":     c["url"],
            "date":    pub_dt.isoformat() if pub_dt else None,
            "summary": desc_zh,
        })
        time.sleep(0.3)  # polite crawling

    return items
