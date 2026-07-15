#!/usr/bin/env python3
"""
Daily scraper for Earnings Whispers 'Top Earnings News' feed.

Hits the internal JSON API directly (no browser, no ads, no login needed):
    GET https://www.earningswhispers.com/api/todaysresults

Run daily via cron, e.g.:
    0 7 * * * /usr/bin/python3 /path/to/scrape_earnings_news.py >> /path/to/ew_scrape.log 2>&1
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://www.earningswhispers.com/api/todaysresults"
OUTPUT_DIR = Path(__file__).parent / "data"
TIMEOUT_SECONDS = 15

HEADERS = {
    # Mimic a normal browser request; some APIs 403 on missing UA / referer.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.earningswhispers.com/earningsnews",
    "Accept": "application/json, text/plain, */*",
}


def fetch_news() -> list[dict]:
    resp = requests.get(API_URL, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        raise ValueError(f"Unexpected response shape: {type(data)}")
    return data


def save_news(items: list[dict]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = OUTPUT_DIR / f"earnings_news_{today}.json"
    out_path.write_text(json.dumps(items, indent=2))
    update_manifest(today)
    return out_path


def update_manifest(today: str) -> None:
    """Maintain data/manifest.json — a sorted list of dates with data,
    so index.html knows what files exist (GitHub Pages has no directory listing)."""
    manifest_path = OUTPUT_DIR / "manifest.json"
    dates = set()
    if manifest_path.exists():
        dates = set(json.loads(manifest_path.read_text()))
    dates.add(today)
    manifest_path.write_text(json.dumps(sorted(dates, reverse=True), indent=2))


def main() -> int:
    try:
        items = fetch_news()
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    out_path = save_news(items)
    print(f"Fetched {len(items)} items -> {out_path}")

    # Quick preview of first few tickers
    for item in items[:5]:
        print(f"  {item.get('ticker', '?'):6s} {item.get('name', '')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
