# earnings-whispers-news-scraper

Pulls the daily "Top Earnings News" feed from Earnings Whispers by calling their
internal JSON API directly (`/api/todaysresults`) — no browser automation, no
ads, no login required.

## Local usage

```bash
pip install -r requirements.txt
python scraper.py
```

Writes `data/earnings_news_YYYY-MM-DD.json`.

## Automatic daily runs (GitHub Actions)

`.github/workflows/daily_scrape.yml` runs the scraper daily via GitHub's
scheduler and commits the new JSON file back to `data/`. No server required.

- Default schedule: 11:00 UTC (7:00 AM ET) — edit the `cron` line to change it.
- You can also trigger it manually from the repo's **Actions** tab
  ("Run workflow").
- Results land as new commits under `data/`.

## Notes / things to verify

- The API endpoint was found via browser DevTools (Network tab) and may
  change without notice if Earnings Whispers updates their frontend. If the
  scraper starts failing, re-check the endpoint the same way.
- No auth was required to hit this endpoint, but if you start getting
  403s, the `User-Agent`/`Referer` headers in `scraper.py` may need updating.
- `todaysresults` appears to return a rolling window of recent items, not
  strictly "just today" — dedupe against previous days' files if you need
  exact-day filtering.
