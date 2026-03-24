"""
财新 — JSON Feed via https://leafduo.com/caixin-feed/feed.json
Returns articles published within the last 7 days, including summary.
"""
from datetime import datetime, timedelta, timezone
import requests

FEED_URL = "https://leafduo.com/caixin-feed/feed.json"
CUTOFF_DAYS = 7

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InfoAggre/1.0)",
    "Accept": "application/feed+json, application/json",
}


def fetch():
    resp = requests.get(FEED_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    items = []

    for entry in data.get("items", []):
        title    = (entry.get("title") or "").strip()
        url      = (entry.get("url") or "").strip()
        date_str = entry.get("date_published") or ""
        summary  = (entry.get("summary") or "").strip()

        if not title or not url:
            continue

        try:
            pub_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if pub_dt < cutoff:
                continue
            date_iso = pub_dt.isoformat()
        except Exception:
            date_iso = None

        items.append({
            "title":   title,
            "url":     url,
            "date":    date_iso,
            "summary": summary or None,
        })

    return items
