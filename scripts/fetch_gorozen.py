"""
Gorozen & Rozencwajg blog — scrape listing page, filter last 30 days,
translate title + description to Chinese.
"""
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
}
BASE_URL = "https://blog.gorozen.com/blog"
CUTOFF   = datetime.now(timezone.utc) - timedelta(days=30)


def _translate(texts: list[str]) -> list[str]:
    """Batch-translate a list of English strings to Simplified Chinese."""
    try:
        from deep_translator import GoogleTranslator
        tr = GoogleTranslator(source="en", target="zh-CN")
        return [tr.translate(t) if t else t for t in texts]
    except Exception as e:
        print(f"  [gorozen] translation error: {e}")
        return texts  # fall back to English


def _parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    results = []
    for card in soup.find_all(class_="custom-post-item"):
        # URL + title
        a = card.select_one("h3 a") or card.select_one(".listing-content a")
        if not a:
            continue
        url   = a["href"].strip()
        title = a.get_text(strip=True)

        # Date — format: MM/DD/YYYY
        date_el = card.select_one(".value_m")
        if not date_el:
            continue
        raw_date = date_el.get_text(strip=True)
        try:
            pub_dt = datetime.strptime(raw_date, "%m/%d/%Y").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue

        if pub_dt < CUTOFF:
            continue  # too old

        # Description
        desc_el = card.select_one(".post_description")
        desc = desc_el.get_text(strip=True) if desc_el else ""

        results.append({
            "url":      url,
            "title":    title,
            "summary":  desc,
            "date":     pub_dt.isoformat(),
            "_raw_date": pub_dt,
        })
    return results


def fetch() -> list[dict]:
    items = []
    # Scrape page 1 (usually enough for 30 days given ~monthly posting cadence)
    for page in range(1, 4):
        url = BASE_URL if page == 1 else f"{BASE_URL}/page/{page}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  [gorozen] page {page} error: {e}")
            break
        parsed = _parse_page(resp.text)
        items.extend(parsed)
        # If last item on page is older than cutoff, no need to paginate further
        if parsed and parsed[-1]["_raw_date"] < CUTOFF:
            break
        if not parsed:
            break

    # Remove helper key
    for it in items:
        it.pop("_raw_date", None)

    if not items:
        return []

    # Translate titles and descriptions in batch
    titles = [it["title"]   for it in items]
    descs  = [it["summary"] for it in items]
    cn_titles = _translate(titles)
    cn_descs  = _translate(descs)
    for it, t, d in zip(items, cn_titles, cn_descs):
        it["title"]   = t
        it["summary"] = d

    print(f"  [gorozen] {len(items)} articles (last 30 days)")
    return items
