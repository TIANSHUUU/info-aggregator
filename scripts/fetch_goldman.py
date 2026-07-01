"""
高盛 Goldman Sachs Insights — 最新文章（中文标题 + 中文摘要）。

Goldman /insights 首页文章正文是 JS 渲染抓不到，但页面的 __NEXT_DATA__ 内嵌 JSON
含文章元数据（title / description / publishDate / url）。解析它，过滤出文字文章、
只留最近一年内的，取最新几篇，标题+摘要用 Google 翻译成中文（同 fetch_schwab）。
"""
import json
import re
from datetime import datetime, timezone, timedelta
import requests

LIST_URL = "https://www.goldmansachs.com/insights"
BASE_URL = "https://www.goldmansachs.com"
MAX_ITEMS = 8
CUTOFF_DAYS = 365
# 排除播客/视频/访谈，只留文字文章
EXCLUDE = ("goldman-sachs-exchanges", "/videos/", "talks-at-gs")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _parse_dt(pd):
    if not isinstance(pd, str):
        return None
    for parse in (
        lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")),
        lambda s: datetime.strptime(s[:10], "%Y-%m-%d"),
    ):
        try:
            dt = parse(pd)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def _translate_to_zh(text, session):
    """Translate English text to Chinese using Google Translate (unofficial, free)."""
    if not text:
        return None
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": text[:500]}
        resp = session.get(url, params=params, timeout=10)
        data = resp.json()
        translated = "".join(part[0] for part in data[0] if part[0])
        return translated.strip() or None
    except Exception:
        return None


def fetch():
    session = requests.Session()
    resp = session.get(LIST_URL, headers=HEADERS, timeout=25)
    resp.raise_for_status()

    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
    if not m:
        return []
    data = json.loads(m.group(1))

    # 递归收集含 publishDate + title + description + 字符串 url(/insights/) 的条目
    found = []

    def walk(o):
        if isinstance(o, dict):
            pd = o.get("publishDate") or o.get("publishedDate")
            title = o.get("title") or o.get("headline")
            desc = o.get("description") or o.get("summary") or o.get("abstract")
            url = o.get("url") or o.get("slug") or o.get("path")
            if (pd and isinstance(title, str) and title.strip()
                    and desc and isinstance(url, str) and "/insights/" in url):
                found.append({
                    "title": title.strip(),
                    "desc": str(desc).strip(),
                    "url": url,
                    "date": pd,
                })
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)

    # 过滤多媒体 + 去重 + 只留最近一年
    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    seen = set()
    items = []
    for f in found:
        if any(x in f["url"] for x in EXCLUDE) or f["title"] in seen:
            continue
        dt = _parse_dt(f["date"])
        if dt is None or dt < cutoff:
            continue
        seen.add(f["title"])
        f["_dt"] = dt
        items.append(f)

    # 按日期降序取最新
    items.sort(key=lambda x: x["_dt"], reverse=True)
    items = items[:MAX_ITEMS]

    # 绝对化 url + 翻译（失败回退英文）
    out = []
    for f in items:
        url = BASE_URL + f["url"] if f["url"].startswith("/") else f["url"]
        title_zh = _translate_to_zh(f["title"], session) or f["title"]
        summary_zh = _translate_to_zh(f["desc"], session) or f["desc"]
        out.append({"title": title_zh, "url": url, "date": f["date"], "summary": summary_zh})

    return out
