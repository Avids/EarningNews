# Earnings Screenshot to Telegram Integration Guide

## Overview
This guide shows how to integrate the earnings screenshot generator into your `xtrack` repo to automatically post earnings reports to Telegram.

## Step 1: Copy Files to xtrack Repo

Copy these files from EarningNews to your xtrack repo:
- `earnings_screenshot.py` - Core screenshot generator
- `telegram_poster.py` - Telegram integration

Or import them as a module (recommended for xtrack).

## Step 2: Install Dependencies

```bash
pip install playwright requests
python -m playwright install chromium
```

## Step 3: Get Telegram Bot Credentials

1. **Create Bot** (if you don't have one):
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow prompts, get your **BOT_TOKEN**

2. **Get Group Chat ID**:
   - Add bot to your Telegram group
   - Send a test message in the group
   - Visit: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   - Find `chat.id` value (negative number) - this is your **CHAT_ID**

## Step 4: Set Up GitHub Secrets

In your xtrack repo settings:
- Add `TELEGRAM_BOT_TOKEN` = your bot token
- Add `TELEGRAM_CHAT_ID` = your group chat ID

## Step 5: Create GitHub Actions Workflow

Create `.github/workflows/post-earnings.yml`:

```yaml
name: Post Earnings to Telegram

on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  post-earnings:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install playwright requests
          python -m playwright install chromium
      
      - name: Copy earnings scripts
        run: |
          curl -o earnings_screenshot.py https://raw.githubusercontent.com/Avids/EarningNews/main/earnings_screenshot.py
          curl -o telegram_poster.py https://raw.githubusercontent.com/Avids/EarningNews/main/telegram_poster.py
      
      - name: Post earnings to Telegram
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python telegram_poster.py
```

## Step 6: Usage in Python

If you want to call it directly from your xtrack code:

```python
from telegram_poster import post_earnings_to_telegram

# Post to Telegram
success = post_earnings_to_telegram(
    telegram_token="your-bot-token",
    chat_id="-your-chat-id"
)

if success:
    print("Posted successfully!")
else:
    print("Failed to post")
```

## Quick Start (Single Command)

```bash
TELEGRAM_BOT_TOKEN="your-token" \
TELEGRAM_CHAT_ID="your-chat-id" \
python telegram_poster.py
```

## Troubleshooting

### "Module not found" error
```bash
python -m pip install --upgrade pip
pip install -r requirements-telegram.txt
python -m playwright install
```

### Telegram API errors
- **Bot token incorrect**: Verify token from @BotFather
- **Chat ID wrong**: Make sure it's the GROUP chat ID (negative number), not private
- **Bot not in group**: Add the bot to the group first

### Screenshot is blank/partial
- Try increasing viewport size in `earnings_screenshot.py`
- Add more wait time: `await page.wait_for_load_state("networkidle")`

## Customization

### Change screenshot dimensions
In `earnings_screenshot.py`, line with `set_viewport_size`:
```python
await page.set_viewport_size({"width": 1400, "height": full_height})  # Make wider
```

### Add custom caption
In `telegram_poster.py`, line with `caption`:
```python
data = {
    "chat_id": chat_id,
    "caption": "📊 Latest Earnings Reports\n\nUpdated at " + datetime.now().strftime("%H:%M UTC")
}
```

### Post to multiple groups
```python
chat_ids = ["-group1_id", "-group2_id", "-group3_id"]
for chat_id in chat_ids:
    post_earnings_to_telegram(token, chat_id)
```

## Files Generated

The script generates screenshots in the `screenshots/` folder:
```
screenshots/
  earnings_2026-07-15_093045.png
  earnings_2026-07-15_153021.png
```

These are automatically cleaned up after posting to Telegram.

---

**Questions?** Check the source code in `earnings_screenshot.py` and `telegram_poster.py` for inline documentation.
