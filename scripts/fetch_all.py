#!/usr/bin/env python3
"""
Main entry point: fetch all sources and write JSON to public/data/.
Run from project root: python scripts/fetch_all.py
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add scripts directory to path so we can import sibling modules
sys.path.insert(0, str(Path(__file__).parent))

import fetch_initium
import fetch_caixin
import fetch_schwab
import fetch_hket
import fetch_stocks

DATA_DIR = Path(__file__).parent.parent / "public" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def run_fetcher(name, func):
    try:
        items = func()
        print(f"[{name}] OK — {len(items)} items")
        return items
    except Exception as e:
        print(f"[{name}] ERROR — {e}", file=sys.stderr)
        return []


def main():
    sources = {
        "initium": fetch_initium.fetch,
        "caixin":  fetch_caixin.fetch,
        "schwab":  fetch_schwab.fetch,
        "hket":    fetch_hket.fetch,
    }

    for key, func in sources.items():
        items = run_fetcher(key, func)
        path = DATA_DIR / f"{key}.json"
        path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    # Stocks
    stocks = run_fetcher("stocks", fetch_stocks.fetch)
    (DATA_DIR / "stocks.json").write_text(
        json.dumps(stocks, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Write metadata
    meta = {"updated_at": datetime.now(timezone.utc).isoformat()}
    (DATA_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[meta] updated_at={meta['updated_at']}")


if __name__ == "__main__":
    main()
