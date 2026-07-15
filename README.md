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
scheduler and commits the new JSON file (plus an updated `data/manifest.json`)
back to the repo. No server required.

- Schedule: 23:00 UTC = 6:00 PM EST. GitHub Actions cron is always UTC and
  does not shift for daylight saving, so during EDT (roughly Mar–Nov) this
  actually fires at 7:00 PM local time. If you want it pinned to 6:00 PM
  EDT in summer instead, change the cron to `0 22 * * *`. There's no single
  cron expression that stays at exactly 6:00 PM year-round across the DST
  switch.
- You can also trigger it manually from the repo's **Actions** tab
  ("Run workflow").

## Publishing the results (`index.html`)

`index.html` is a static page that lists available dates (from
`data/manifest.json`) and shows tickers/names for the selected date. It fetches
JSON client-side — no build step.

To publish via GitHub Pages:
1. Repo **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)`
4. Save — your page will be live at `https://<username>.github.io/<repo>/`

Each day's Actions run commits new data, and the published page picks it up
automatically (it fetches the JSON fresh on every page load).

## Notes / things to verify

- The API endpoint was found via browser DevTools (Network tab) and may
  change without notice if Earnings Whispers updates their frontend. If the
  scraper starts failing, re-check the endpoint the same way.
- No auth was required to hit this endpoint, but if you start getting
  403s, the `User-Agent`/`Referer` headers in `scraper.py` may need updating.
- `todaysresults` appears to return a rolling window of recent items, not
  strictly "just today" — dedupe against previous days' files if you need
  exact-day filtering.
