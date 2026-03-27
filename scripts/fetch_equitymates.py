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
GROQ_MODEL  = "qwen/qwen3-32b"


def _get_latest_episode_url() -> tuple[str, str, str]:
    """Return (url, title, date_iso) for the most recent episode."""
    resp = requests.get(LISTING_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Episode cards use <a class="card-link" href="/episode/..."> (anchor is empty, title in sibling h4)
    cards = soup.select("a.card-link[href*='/episode/']")
    if not cards:
        # Fallback: any anchor with /episode/ in href
        cards = soup.select("a[href*='/episode/']")
    if not cards:
        raise ValueError("Could not find episode link on listing page")

    card = cards[0]
    url = card["href"]
    # Title is in the sibling h4 inside the same card wrapper
    wrapper = card.find_next("h4")
    title = wrapper.get_text(strip=True) if wrapper else ""
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
    prompt = f"""以下是一集澳大利亚投资播客的文字稿。

请用中文输出JSON格式的节目总结：
{{"sections":[{{"heading":"标题","points":["要点"]}}],"stocks":["名称(代码)"]}}

硬性规定——每个要点必须满足以下至少一条：
A) 包含具体数字（比例/金额/时间/规模）
B) 描述一个明确的因果机制（因为X，所以Y）
C) 呈现一个反直觉的结论（违反常识的发现）

违反此规定的要点一律不写，宁缺毋滥。最多4个section，每section 2-4个要点。
stocks只列嘉宾深入分析过的证券，不列随口提到的。
输出纯JSON，不加markdown代码块，不加<think>标签。

Transcript:
{episode['transcript']}"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    raw = resp.choices[0].message.content.strip()
    # Strip Qwen3 <think>...</think> reasoning blocks and markdown fences
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    data = json.loads(raw)
    return data


def fetch() -> dict:
    """Return a single dict (not a list) with the latest episode summary."""
    print(f"  [equitymates] GROQ_API_KEY set: {bool(os.environ.get('GROQ_API_KEY'))}")
    url, _, _ = _get_latest_episode_url()
    print(f"  [equitymates] latest episode URL: {url}")
    episode   = _get_episode_data(url)
    print(f"  [equitymates] transcript length: {len(episode['transcript'])}")

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
