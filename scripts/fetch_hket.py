"""
香港經濟日報 (HKET) 兩岸新聞 — RSS feed https://www.hket.com/rss/china

改用官方 RSS：原先抓 HTML 列表页 (china.hket.com/srac002/...) 会被 HKET 反爬
对数据中心 IP（GitHub Actions）返回 405，导致 CI 抓到空。RSS 端点对聚合器友好，
且自带 pubDate（原 HTML 抓法 date 恒为 null）。对标 fetch_initium.py 的 RSS 写法。
"""
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
import requests

RSS_URL = "https://www.hket.com/rss/china"

# 用完整浏览器 UA：HKET 对简化/bot UA 会返回 403。
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.hket.com/rss",
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
