"""
香港經濟日報 (HKET) 兩岸新聞 — 经 Cloudflare Worker 代抓「即時中國」HTML 列表页。

HKET 反爬封数据中心 IP（CI 直连 HTML/RSS 均 405），而其 RSS 内容又极稀少。
故由项目自有的 Cloudflare Worker（出口未被封）代抓内容丰富的 HTML 列表页，
CI 解析其中的 /article/ 链接。HTML 列表页不含发布时间，故 date 为 None。
"""
import re
import requests
from bs4 import BeautifulSoup

# Worker /hket 路由代抓 HKET HTML 列表页（见 worker/trigger-refresh.js）
PAGE_URL = "https://infoaggre-refresh.tianshu-tan.workers.dev/hket"
BASE_URL = "https://china.hket.com"

HEADERS = {
    "User-Agent": "infoaggre-fetch/1.0 (+https://github.com/TIANSHUUU/info-aggregator)",
    "Accept": "text/html, */*",
}


def fetch():
    resp = requests.get(PAGE_URL, headers=HEADERS, timeout=25)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    seen = set()

    # HKET article links follow pattern /article/XXXXXXX/...
    article_pattern = re.compile(r"^/article/\d+")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not article_pattern.match(href):
            continue

        url = BASE_URL + href if href.startswith("/") else href
        title = a.get_text(strip=True)

        if len(title) < 8 or url in seen:
            continue
        seen.add(url)

        items.append({"title": title, "url": url, "date": None})

    return items
