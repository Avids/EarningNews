"""
Integration example for xtrack Telegram posting workflow
Add this to your xtrack repo to automatically post earnings reports to Telegram
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_earnings_screenshot() -> Optional[Path]:
    """
    Fetch and generate latest earnings screenshot
    Returns path to PNG file or None if failed
    """
    try:
        # Call the earnings_screenshot.py from EarningNews repo
        result = subprocess.run(
            [sys.executable, "-m", "earnings_screenshot"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            screenshot_path = Path(result.stdout.strip())
            if screenshot_path.exists():
                return screenshot_path
        else:
            print(f"[ERROR] Screenshot generation failed: {result.stderr}")
        
        return None
    except Exception as e:
        print(f"[ERROR] Failed to generate screenshot: {e}")
        return None


def post_earnings_to_telegram(telegram_token: str, chat_id: str) -> bool:
    """
    Generate earnings screenshot and post to Telegram
    
    Args:
        telegram_token: Your Telegram Bot token (from @BotFather)
        chat_id: Telegram group/channel ID
    
    Returns:
        True if successfully posted, False otherwise
    """
    import requests
    
    # Generate screenshot
    screenshot_path = get_earnings_screenshot()
    if not screenshot_path:
        print("[ERROR] Could not generate earnings screenshot")
        return False
    
    # Post to Telegram
    try:
        with open(screenshot_path, "rb") as img_file:
            files = {"photo": img_file}
            data = {
                "chat_id": chat_id,
                "caption": "📊 Latest Earnings Reports"
            }
            
            response = requests.post(
                f"https://api.telegram.org/bot{telegram_token}/sendPhoto",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"[SUCCESS] Posted to Telegram: {chat_id}")
                return True
            else:
                print(f"[ERROR] Telegram API error: {response.status_code} - {response.text}")
                return False
    
    except Exception as e:
        print(f"[ERROR] Failed to post to Telegram: {e}")
        return False


# Example usage in GitHub Actions or cron job:
if __name__ == "__main__":
    import os
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not telegram_token or not telegram_chat_id:
        print("[ERROR] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables")
        sys.exit(1)
    
    success = post_earnings_to_telegram(telegram_token, telegram_chat_id)
    sys.exit(0 if success else 1)
