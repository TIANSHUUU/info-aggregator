"""
明报 中国新闻 — https://news.mingpao.com/pns/中國/section/YYYYMMDD/s00013
URL contains today's date dynamically. Returns article titles + links.
"""
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://news.mingpao.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Referer": "https://news.mingpao.com/",
}

# HKT is UTC+8
HKT_OFFSET = 8


def _today_hkt() -> str:
    """Return today's date in HKT as YYYYMMDD string."""
    from datetime import timezone, timedelta
    hkt = timezone(timedelta(hours=HKT_OFFSET))
    return datetime.now(hkt).strftime("%Y%m%d")


def fetch():
    date_str = _today_hkt()
    page_url = (
        f"{BASE_URL}/pns/%E4%B8%AD%E5%9C%8B/section/{date_str}/s00013"
    )

    resp = requests.get(page_url, headers=HEADERS, timeout=25)
    resp.raise_for_status()

    soup  = BeautifulSoup(resp.text, "html.parser")
    items = []
    seen  = set()

    # 明报 article links: /pns/中國/news/YYYYMMDD/...
    article_pattern = re.compile(r"^/pns/[^/]+/news/\d{8}/")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not article_pattern.match(href):
            continue

        url   = BASE_URL + href if href.startswith("/") else href
        title = a.get_text(strip=True)

        if len(title) < 5 or url in seen:
            continue
        seen.add(url)

        items.append({"title": title, "url": url, "date": None})

    return items
