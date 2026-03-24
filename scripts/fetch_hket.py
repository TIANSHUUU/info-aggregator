"""
香港经济日报 (HKET) 即时中国 — https://china.hket.com/srac002/即時中國
Returns all article titles + links found on the listing page.
"""
import re
import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://china.hket.com/srac002/%E5%8D%B3%E6%99%82%E4%B8%AD%E5%9C%8B"
BASE_URL  = "https://china.hket.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
    "Referer": "https://china.hket.com/",
}


def fetch():
    resp = requests.get(PAGE_URL, headers=HEADERS, timeout=25)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    seen  = set()

    # HKET article links follow pattern /article/XXXXXXX/...
    article_pattern = re.compile(r"^/article/\d+")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not article_pattern.match(href):
            continue

        url   = BASE_URL + href if href.startswith("/") else href
        title = a.get_text(strip=True)

        # Skip navigation / short strings
        if len(title) < 8 or url in seen:
            continue
        seen.add(url)

        items.append({"title": title, "url": url, "date": None})

    return items
