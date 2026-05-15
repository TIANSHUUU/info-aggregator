"""
Peak Prosperity Podcast — latest episode summary via Groq.

Uses Blubrry RSS feed to get episode metadata + description.
Scrapes peakprosperity.com article page for visible pre-paywall content.
Falls back to RSS description if scraping fails.
"""
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

RSS_URL    = "https://feeds.blubrry.com/feeds/1469494.xml"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MODEL_FALLBACK = "llama-3.1-8b-instant"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _get_rss_episode() -> dict:
    """Get latest episode metadata + description from RSS feed."""
    resp = requests.get(RSS_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "xml")
    item = soup.find("item")
    if not item:
        raise ValueError("No items in RSS feed")

    title = item.find("title").get_text(strip=True) if item.find("title") else ""
    pub   = item.find("pubDate").get_text(strip=True) if item.find("pubDate") else ""
    link  = item.find("link").get_text(strip=True) if item.find("link") else ""
    # Strip UTM params from link
    link  = link.split("?")[0] if link else ""

    desc_tag = item.find("description") or item.find("itunes:summary") or {}
    desc_html = desc_tag.get_text(strip=True) if hasattr(desc_tag, "get_text") else ""
    desc_text = BeautifulSoup(desc_html, "lxml").get_text(separator="\n", strip=True)

    try:
        dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %z")
        date_iso = dt.isoformat()
    except ValueError:
        date_iso = pub

    return {"title": title, "date": date_iso, "url": link, "desc": desc_text}


def _scrape_article(url: str) -> str:
    """Scrape visible article text from peakprosperity.com (pre-paywall content)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        # Try common article content selectors
        for selector in ["article", ".entry-content", ".post-content", "main"]:
            el = soup.select_one(selector)
            if el:
                # Remove script/style/paywall elements
                for tag in el.find_all(["script", "style", "aside", "nav"]):
                    tag.decompose()
                text = el.get_text(separator="\n", strip=True)
                if len(text) > 200:
                    return text[:8000]
    except Exception as e:
        print(f"  [peakprosperity] article scrape failed: {e}")
    return ""


def _summarise(content: str, title: str) -> dict:
    """Call Groq to generate structured Chinese summary."""
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)
    prompt = f"""你是一个经济和投资内容分析师。以下是一集关于经济、能源、地缘政治的播客内容。

请用中文生成结构化总结，输出严格JSON格式（不要加markdown代码块，不要加注释）：
{{"sections":[{{"heading":"章节标题","points":["要点1","要点2","要点3"]}}],"stocks":["资产名称或代码"]}}

要求：
- 每个主要话题一个section（2-4个section）
- 每section 2-4个要点，要具体，包含数字和关键细节
- 投资洞察/风险提示要明确标出
- stocks列出所有提及的资产/商品/ETF，格式：名称(代码)，若无则返回空数组

内容：
{content}"""

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
    except Exception as e:
        if "rate_limit" in str(e) or "429" in str(e) or "413" in str(e):
            print(f"  [peakprosperity] primary model limit hit, falling back to {GROQ_MODEL_FALLBACK}")
            resp = client.chat.completions.create(
                model=GROQ_MODEL_FALLBACK,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
        else:
            raise
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    # Extract first JSON object in case model adds surrounding text
    m = re.search(r'\{.*\}', raw, flags=re.DOTALL)
    raw = m.group(0) if m else raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [peakprosperity] JSON parse error: {e} — raw: {raw[:200]}")
        raise


def fetch() -> dict:
    """Return a single dict with the latest episode summary."""
    print(f"  [peakprosperity] GROQ_API_KEY set: {bool(os.environ.get('GROQ_API_KEY'))}")

    ep = _get_rss_episode()
    print(f"  [peakprosperity] latest: {ep['title']}")

    # Try to get more content from the article page
    article_text = _scrape_article(ep["url"]) if ep["url"] else ""
    if article_text:
        print(f"  [peakprosperity] article text: {len(article_text)} chars")
        content = article_text
    else:
        print(f"  [peakprosperity] falling back to RSS description ({len(ep['desc'])} chars)")
        content = ep["desc"]

    if not content or len(content) < 50:
        print("  [peakprosperity] insufficient content, skipping summarisation")
        return {"title": ep["title"], "date": ep["date"], "url": ep["url"],
                "sections": [], "stocks": []}

    try:
        summary = _summarise(content, ep["title"])
    except Exception as e:
        print(f"  [peakprosperity] summarisation failed: {e}")
        summary = {"sections": [], "stocks": []}

    print(f"  [peakprosperity] {len(summary.get('sections', []))} sections")

    return {
        "title":    ep["title"],
        "date":     ep["date"],
        "url":      ep["url"],
        "sections": summary.get("sections", []),
        "stocks":   summary.get("stocks", []),
    }
