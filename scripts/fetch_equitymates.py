"""
Equity Mates Investing Podcast — latest episode transcript summary via Groq.

Cloudflare blocks GitHub Actions IPs on equitymates.com.
Strategy:
  1. curl_cffi (Chrome TLS fingerprint) → bypasses Cloudflare bot detection
  2. Acast RSS → get episode URL + show notes as fallback content
"""
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

ACAST_RSS  = "https://feeds.acast.com/public/shows/8c560a52-84ff-4b06-b819-f4e9bd6e85ef"
GROQ_MODEL = "llama-3.3-70b-versatile"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-AU,en;q=0.9",
}


def _cf_get(url: str) -> "requests.Response":
    """Fetch URL using Chrome TLS fingerprint to bypass Cloudflare."""
    from curl_cffi import requests as cffi_req
    return cffi_req.get(url, impersonate="chrome120", timeout=20)


def _get_acast_episode() -> dict:
    """Get latest episode metadata + description from Acast RSS (always accessible)."""
    resp = requests.get(ACAST_RSS, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "xml")
    item = soup.find("item")
    if not item:
        raise ValueError("No items in Acast RSS")

    title   = item.find("title").get_text(strip=True) if item.find("title") else ""
    pub     = item.find("pubDate").get_text(strip=True) if item.find("pubDate") else ""
    # Acast episode URL → derive equitymates.com URL via slug
    acast_url  = item.find("link").get_text(strip=True) if item.find("link") else ""
    acast_slug = acast_url.rstrip("/").split("/")[-1]  # e.g. "is-your-portfolio-..."

    # Description from Acast RSS (HTML-encoded)
    desc_raw = item.find("description") or item.find("itunes:summary") or {}
    desc_html = desc_raw.get_text(strip=True) if hasattr(desc_raw, "get_text") else ""
    desc_text = BeautifulSoup(desc_html, "lxml").get_text(separator="\n", strip=True)

    try:
        dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
        date_iso = dt.isoformat()
    except ValueError:
        date_iso = pub

    return {
        "title":      title,
        "date":       date_iso,
        "acast_url":  acast_url,
        "acast_slug": acast_slug,
        "desc":       desc_text,
    }


def _find_equitymates_url(acast_slug: str) -> str:
    """Find the equitymates.com episode URL by searching their site via WP API (curl_cffi)."""
    try:
        resp = _cf_get(
            f"https://equitymates.com/wp-json/wp/v2/episode?per_page=1&orderby=date&order=desc"
        )
        if resp.status_code == 200:
            ep = resp.json()[0]
            return ep.get("link", "")
    except Exception as e:
        print(f"  [equitymates] WP API via curl_cffi failed: {e}")
    return ""


def _get_transcript(url: str) -> str:
    """Fetch equitymates episode page and extract transcript via curl_cffi."""
    try:
        resp = _cf_get(url)
        if resp.status_code != 200:
            print(f"  [equitymates] episode page status: {resp.status_code}")
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        div  = soup.find(id="transcript")
        return div.get_text(separator="\n", strip=True) if div else ""
    except Exception as e:
        print(f"  [equitymates] transcript fetch failed: {e}")
        return ""


def _summarise(content: str, title: str) -> dict:
    """Call Groq Qwen3 to generate structured Chinese summary."""
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)
    prompt = f"""你是一个投资播客内容分析师。以下是一集澳大利亚投资播客的transcript。

请用中文生成结构化总结，输出严格JSON格式（不要加markdown代码块，不要加注释）：
{{"sections":[{{"heading":"章节标题","points":["要点1","要点2","要点3"]}}],"stocks":["股票名称或代码"]}}

要求：
- 每个主要话题一个section（3-5个section）
- 每section 3-5个要点，要具体，包含数字和关键细节
- 投资洞察/建议要明确标出
- stocks列出所有提及的股票/ETF，格式：名称(代码)

Transcript:
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
    """Return a single dict with the latest episode summary."""
    print(f"  [equitymates] GROQ_API_KEY set: {bool(os.environ.get('GROQ_API_KEY'))}")

    # Step 1: get episode metadata from Acast RSS (always works)
    ep = _get_acast_episode()
    print(f"  [equitymates] latest: {ep['title']}")

    # Step 2: find equitymates.com URL via curl_cffi
    em_url = _find_equitymates_url(ep["acast_slug"])
    print(f"  [equitymates] equitymates URL: {em_url or '(not found)'}")

    # Step 3: get full transcript if we have the URL
    transcript = _get_transcript(em_url) if em_url else ""
    if transcript:
        print(f"  [equitymates] transcript: {len(transcript)} chars")
        content = transcript[:28000]
    else:
        print(f"  [equitymates] falling back to Acast description ({len(ep['desc'])} chars)")
        content = ep["desc"]

    if not content or len(content) < 50:
        print("  [equitymates] insufficient content, skipping summarisation")
        return {"title": ep["title"], "date": ep["date"], "url": em_url or ep["acast_url"],
                "sections": [], "stocks": []}

    summary = _summarise(content, ep["title"])
    print(f"  [equitymates] {len(summary.get('sections', []))} sections")

    return {
        "title":    ep["title"],
        "date":     ep["date"],
        "url":      em_url or ep["acast_url"],
        "sections": summary.get("sections", []),
        "stocks":   summary.get("stocks", []),
    }
