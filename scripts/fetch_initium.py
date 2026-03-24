"""
端传媒 (The Initium) — RSS feed https://theinitium.com/rss/
Returns articles published within the last 24 hours.
"""
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
import requests

RSS_URL = "https://theinitium.com/rss/"
CUTOFF_HOURS = 24

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InfoAggre/1.0; +https://github.com/TIANSHUUU/info-aggregator)",
    "Accept": "application/rss+xml, application/xml, text/xml",
}


def fetch():
    resp = requests.get(RSS_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    channel = root.find("channel")
    if channel is None:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)
    items = []

    for item in channel.findall("item"):
        title   = (item.findtext("title") or "").strip()
        link    = (item.findtext("link") or "").strip()
        pub_str = item.findtext("pubDate") or ""

        if not title or not link:
            continue

        try:
            pub_dt = parsedate_to_datetime(pub_str)
            if pub_dt < cutoff:
                continue
            date_iso = pub_dt.isoformat()
        except Exception:
            date_iso = None

        items.append({"title": title, "url": link, "date": date_iso})

    return items
