"""
明报 中国新闻 — https://news.mingpao.com/pns/中國/section/YYYYMMDD/s00013
URL contains today's date. Tries multiple strategies to bypass Cloudflare.
"""
import re
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://news.mingpao.com"
HKT = timezone(timedelta(hours=8))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}

ARTICLE_PATTERN = re.compile(r"^/pns/[^/]+/news/\d{8}/")


def fetch():
    date_str = datetime.now(HKT).strftime("%Y%m%d")
    page_url = f"{BASE_URL}/pns/%E4%B8%AD%E5%9C%8B/section/{date_str}/s00013"

    session = requests.Session()
    # Warm-up request to get cookies (helps bypass basic Cloudflare bot checks)
    try:
        session.get(BASE_URL, headers=HEADERS, timeout=15)
    except Exception:
        pass

    resp = session.get(page_url, headers=HEADERS, timeout=25)
    resp.raise_for_status()

    soup  = BeautifulSoup(resp.text, "html.parser")
    items = []
    seen  = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not ARTICLE_PATTERN.match(href):
            continue
        url   = BASE_URL + href if href.startswith("/") else href
        title = a.get_text(strip=True)
        if len(title) < 5 or url in seen:
            continue
        seen.add(url)
        items.append({"title": title, "url": url, "date": None})

    return items
