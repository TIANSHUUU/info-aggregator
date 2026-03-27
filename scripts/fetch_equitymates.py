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
WP_API_URL = "https://equitymates.com/wp-json/wp/v2/episode?per_page=1&orderby=date&order=desc"
GROQ_MODEL = "qwen/qwen3-32b"


def _get_latest_episode() -> dict:
    """Return episode metadata + show notes via WordPress REST API (bypasses Cloudflare)."""
    resp = requests.get(WP_API_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    ep = resp.json()[0]

    url   = ep["link"]
    title = BeautifulSoup(ep["title"]["rendered"], "lxml").get_text(strip=True)
    date  = ep.get("date", "")
    # ISO date from WP API is already in local time; convert to UTC ISO string
    try:
        dt = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
        date_iso = dt.isoformat()
    except ValueError:
        date_iso = date

    # Show notes as fallback content if transcript page is blocked
    notes_html = ep.get("content", {}).get("rendered", "")
    notes = BeautifulSoup(notes_html, "lxml").get_text(separator="\n", strip=True)

    return {"url": url, "title": title, "date": date_iso, "notes": notes}


def _get_transcript(url: str) -> str:
    """Fetch episode page and extract full transcript. Returns empty string if blocked."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [equitymates] episode page fetch failed ({e}), will use show notes")
        return ""

    soup = BeautifulSoup(resp.text, "lxml")
    transcript_div = soup.find(id="transcript")
    if transcript_div:
        return transcript_div.get_text(separator="\n", strip=True)
    return ""


def _summarise(content: str, title: str) -> dict:
    """Call Groq to generate structured Chinese summary."""
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)
    prompt = f"""以下是一集澳大利亚投资播客的内容（标题：{title}）。

请用中文输出JSON格式的节目总结：
{{"sections":[{{"heading":"标题","points":["要点"]}}],"stocks":["名称(代码)"]}}

硬性规定——每个要点必须满足以下至少一条：
A) 包含具体数字（比例/金额/时间/规模）
B) 描述一个明确的因果机制（因为X，所以Y）
C) 呈现一个反直觉的结论（违反常识的发现）

违反此规定的要点一律不写，宁缺毋滥。最多4个section，每section 2-4个要点。
stocks只列嘉宾深入分析过的证券，不列随口提到的。
输出纯JSON，不加markdown代码块，不加<think>标签。

内容：
{content}"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


def fetch() -> dict:
    """Return a single dict (not a list) with the latest episode summary."""
    print(f"  [equitymates] GROQ_API_KEY set: {bool(os.environ.get('GROQ_API_KEY'))}")

    ep = _get_latest_episode()
    print(f"  [equitymates] latest episode: {ep['title']} — {ep['url']}")

    # Try full transcript first, fall back to show notes
    transcript = _get_transcript(ep["url"])
    if transcript:
        print(f"  [equitymates] using transcript ({len(transcript)} chars)")
        content = transcript[:28000]
    else:
        print(f"  [equitymates] using show notes ({len(ep['notes'])} chars)")
        content = ep["notes"]

    if not content or len(content) < 100:
        print("  [equitymates] insufficient content, skipping summarisation")
        return {"title": ep["title"], "date": ep["date"], "url": ep["url"],
                "sections": [], "stocks": []}

    summary = _summarise(content, ep["title"])
    print(f"  [equitymates] {len(summary['sections'])} sections summarised")

    return {
        "title":    ep["title"],
        "date":     ep["date"],
        "url":      ep["url"],
        "sections": summary.get("sections", []),
        "stocks":   summary.get("stocks", []),
    }
