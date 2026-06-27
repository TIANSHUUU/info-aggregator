"""
香港經濟日報 (HKET) 兩岸新聞 — 经 Cloudflare Worker 代抓 RSS。

HKET 反爬封数据中心/代理 IP（GitHub Actions、jina 等直连 RSS/HTML 均 405），
故通过项目自有的 Cloudflare Worker（出口为 Cloudflare IP，未被封）代抓
https://www.hket.com/rss/china 并原样返回 RSS XML。解析同 fetch_initium.py，
pubDate 转 ISO 日期。
"""
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
import requests

# Worker 的 /hket 路由代抓 HKET RSS（见 worker/trigger-refresh.js）
RSS_URL = "https://infoaggre-refresh.tianshu-tan.workers.dev/hket"

HEADERS = {
    "User-Agent": "infoaggre-fetch/1.0 (+https://github.com/TIANSHUUU/info-aggregator)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def fetch():
    resp = requests.get(RSS_URL, headers=HEADERS, timeout=25)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    channel = root.find("channel")
    if channel is None:
        return []

    items = []
    seen = set()

    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link or link in seen:
            continue
        seen.add(link)

        pub_str = item.findtext("pubDate") or ""
        try:
            date_iso = parsedate_to_datetime(pub_str).isoformat()
        except Exception:
            date_iso = None

        items.append({"title": title, "url": link, "date": date_iso})

    return items
