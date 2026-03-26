"""
Equity Mates Investing Podcast — latest episode transcript summary via Groq.
"""
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}
LISTING_URL = "https://equitymates.com/show/equity-mates-investing-podcast/"
GROQ_MODEL  = "llama-3.3-70b-versatile"


def _get_latest_episode_url() -> tuple[str, str, str]:
    """Return (url, title, date_iso) for the most recent episode."""
    resp = requests.get(LISTING_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Each episode card has an <a> with the episode URL
    card = soup.select_one("article a[href*='/episode/'], .episode a[href*='/episode/'], a[href*='/episode/']")
    if not card:
        raise ValueError("Could not find episode link on listing page")

    url = card["href"]
    title = card.get_text(strip=True) or ""
    return url, title, ""


def _get_episode_data(url: str) -> dict:
    """Fetch episode page and extract title, date, transcript."""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    title = soup.select_one("h1.entry-title, h1")
    title = title.get_text(strip=True) if title else ""

    date_el = soup.select_one(".info-date, .post-date, time")
    date_str = date_el.get_text(strip=True) if date_el else ""
    # Try to parse date like "26 March, 2026" or "March 26, 2026"
    date_iso = ""
    for fmt in ("%d %B, %Y", "%B %d, %Y", "%d %B %Y"):
        try:
            # Strip non-date prefix (e.g., "HOSTS Alec | 26 March, 2026")
            clean = re.sub(r"^.*\|\s*", "", date_str).strip()
            dt = datetime.strptime(clean, fmt).replace(tzinfo=timezone.utc)
            date_iso = dt.isoformat()
            break
        except ValueError:
            continue

    transcript_div = soup.find(id="transcript")
    transcript = transcript_div.get_text(separator="\n", strip=True) if transcript_div else ""

    # Also get stocks from show notes
    stocks_raw = ""
    notes = soup.find(id="notes") or soup.select_one(".tab-pane")
    if notes:
        stocks_match = re.search(r"Stocks.*?mentioned[:\s]*(.*?)(?:\n\n|$)", notes.get_text(), re.DOTALL | re.I)
        if stocks_match:
            stocks_raw = stocks_match.group(1).strip()

    return {"title": title, "date": date_iso, "url": url,
            "transcript": transcript[:28000], "stocks_raw": stocks_raw}


def _summarise(episode: dict) -> dict:
    """Call Groq to generate structured Chinese summary."""
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)
    prompt = f"""你是一个投资播客内容分析师。以下是一集澳大利亚投资播客的transcript。

请用中文生成结构化总结，输出严格JSON格式（不要加markdown代码块，不要加注释）：
{{"sections":[{{"heading":"章节标题","points":["要点1","要点2","要点3"]}}],"stocks":["股票名称或代码"]}}

要求：
- 每个主要话题一个section（3-6个section）
- 每section 3-5个要点，要具体，包含数字和关键细节
- 投资洞察/建议要明确标出
- stocks列出所有提及的股票/ETF，格式：名称(代码)

Transcript:
{episode['transcript']}"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = resp.choices[0].message.content.strip()
    # Strip accidental markdown fences
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    data = json.loads(raw)
    return data


def fetch() -> dict:
    """Return a single dict (not a list) with the latest episode summary."""
    url, _, _ = _get_latest_episode_url()
    episode   = _get_episode_data(url)

    if not episode["transcript"]:
        print("  [equitymates] No transcript found, skipping summarisation")
        return {"title": episode["title"], "date": episode["date"],
                "url": url, "sections": [], "stocks": []}

    summary = _summarise(episode)
    print(f"  [equitymates] {len(summary['sections'])} sections summarised")

    return {
        "title":    episode["title"],
        "date":     episode["date"],
        "url":      url,
        "sections": summary.get("sections", []),
        "stocks":   summary.get("stocks", []),
    }
