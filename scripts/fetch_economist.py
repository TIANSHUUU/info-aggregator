"""
The Economist — weekly epub download from GitHub repo.
Only runs on Fridays. Downloads to ~/Downloads.

Repo: https://github.com/hehonghui/awesome-english-ebooks/tree/master/01_economist
Pattern: te_YYYY.MM.DD / TheEconomist.YYYY.MM.DD.epub
"""
import re
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
import requests

GITHUB_API = "https://api.github.com/repos/hehonghui/awesome-english-ebooks/contents/01_economist"
RAW_BASE   = "https://raw.githubusercontent.com/hehonghui/awesome-english-ebooks/master/01_economist"
DOWNLOAD_DIR = Path.home() / "Downloads"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InfoAggre/1.0)",
    "Accept": "application/vnd.github+json",
}


def _latest_friday_folder():
    """Find the most recent te_YYYY.MM.DD folder via GitHub API."""
    resp = requests.get(GITHUB_API, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    entries = resp.json()

    folders = []
    pattern = re.compile(r"^te_(\d{4})\.(\d{2})\.(\d{2})$")
    for entry in entries:
        if entry.get("type") == "dir":
            m = pattern.match(entry["name"])
            if m:
                folders.append((
                    date(int(m.group(1)), int(m.group(2)), int(m.group(3))),
                    entry["name"],
                ))

    if not folders:
        return None
    folders.sort(key=lambda x: x[0], reverse=True)
    return folders[0][1]  # e.g. "te_2026.03.21"


def run():
    today = date.today()
    # Only run on Fridays (weekday() == 4)
    # GitHub Actions can call this script directly if needed
    if today.weekday() != 4:
        print(f"[economist] Today is {today.strftime('%A')}, not Friday — skipping.")
        return

    folder = _latest_friday_folder()
    if not folder:
        print("[economist] Could not find latest folder.", file=sys.stderr)
        return

    # Derive filename from folder name: te_2026.03.21 -> TheEconomist.2026.03.21.epub
    date_part  = folder.replace("te_", "")            # "2026.03.21"
    epub_name  = f"TheEconomist.{date_part}.epub"
    raw_url    = f"{RAW_BASE}/{folder}/{epub_name}"
    dest_path  = DOWNLOAD_DIR / epub_name

    if dest_path.exists():
        print(f"[economist] Already downloaded: {dest_path}")
        return

    print(f"[economist] Downloading {epub_name} …")
    resp = requests.get(raw_url, stream=True, timeout=60)
    resp.raise_for_status()

    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = dest_path.stat().st_size / 1_048_576
    print(f"[economist] Saved to {dest_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    run()
