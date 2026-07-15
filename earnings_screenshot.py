#!/usr/bin/env python3
"""
Earnings News Screenshot Generator
Fetches latest earnings data from EarningNews repo and generates a PNG screenshot
Ready to post to Telegram
"""

import json
import re
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiohttp
import requests
from playwright.async_api import async_playwright


GITHUB_RAW_URL = "https://raw.githubusercontent.com/Avids/EarningNews/main"
OUTPUT_DIR = Path(__file__).parent / "screenshots"


def fetch_latest_date() -> Optional[str]:
    """Fetch the latest date from manifest.json"""
    try:
        resp = requests.get(f"{GITHUB_RAW_URL}/data/manifest.json", timeout=10)
        resp.raise_for_status()
        dates = resp.json()
        return dates[0] if dates else None
    except Exception as e:
        print(f"[ERROR] Failed to fetch manifest: {e}")
        return None


def fetch_earnings_data(date: str) -> Optional[list]:
    """Fetch earnings data for a specific date"""
    try:
        resp = requests.get(
            f"{GITHUB_RAW_URL}/data/earnings_news_{date}.json",
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch earnings data for {date}: {e}")
        return None


def format_number(value, decimals=2, currency=False):
    """Format number with commas and optional currency"""
    if value is None:
        return "-"
    
    try:
        num = float(value)
        formatted = f"{num:,.{decimals}f}"
        return f"${formatted}" if currency else formatted
    except (ValueError, TypeError):
        return "-"


def format_percentage(value):
    """Format as percentage"""
    if value is None:
        return "-"
    
    try:
        return f"{float(value) * 100:.2f}%"
    except (ValueError, TypeError):
        return "-"


def get_surprise_badge(label, value):
    """Generate HTML badge for surprise indicator"""
    if value is None:
        return ""
    
    threshold = 0.005
    if value > threshold:
        return f'<span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">▲ {label}</span>'
    elif value < -threshold:
        return f'<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">▼ {label}</span>'
    else:
        return f'<span style="background: #f5f5f5; color: #171717; padding: 1px 7px; border-radius: 12px; font-size: 11px; font-weight: 500;">▬ {label}</span>'


def generate_html(date: str, items: list) -> str:
    """Generate HTML for earnings report"""
    
    rows = ""
    for item in items:
        eps = format_number(item.get("eps"))
        earnings_growth = format_percentage(item.get("earningsGrowth"))
        revenue_growth = format_percentage(item.get("revenueGrowth"))
        
        eps_badge = get_surprise_badge("EPS", item.get("earningsSurprise"))
        rev_badge = get_surprise_badge("Rev", item.get("revenueSurprise"))
        badges = f"{eps_badge} {rev_badge}".strip()
        
        rows += f"""
        <tr style="border-bottom: 1px solid #e5e5e5;">
            <td style="padding: 12px; text-align: left;">
                <span style="background: #171717; color: #fafafa; border-radius: 12px; padding: 2px 8px; font-size: 11px; font-weight: 600;">
                    {item.get('ticker', '-')}
                </span>
            </td>
            <td style="padding: 12px; text-align: left; color: #0a0a0a; font-weight: 500;">
                {item.get('name', '-')}
            </td>
            <td style="padding: 12px; text-align: left;">
                {badges}
            </td>
            <td style="padding: 12px; text-align: left;">{eps}</td>
            <td style="padding: 12px; text-align: left;">{earnings_growth}</td>
            <td style="padding: 12px; text-align: left;">{revenue_growth}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: white;
                margin: 0;
                padding: 24px;
                color: #0a0a0a;
            }}
            .header {{
                margin-bottom: 24px;
                border-bottom: 2px solid #e5e5e5;
                padding-bottom: 16px;
            }}
            .header h2 {{
                margin: 0 0 8px;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            .header p {{
                margin: 0;
                color: #737373;
                font-size: 14px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            thead {{
                background: #fafafa;
            }}
            th {{
                text-align: left;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #737373;
                border-bottom: 1px solid #e5e5e5;
            }}
            td {{
                padding: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Earnings Reports</h2>
            <p>Data as of {date}</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Name</th>
                    <th>Surprise / Guidance</th>
                    <th>EPS (actual)</th>
                    <th>Earnings Growth (YoY)</th>
                    <th>Revenue Growth (YoY)</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html


async def generate_screenshot(html: str, output_path: Path) -> bool:
    """Generate screenshot from HTML using Playwright"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1200, "height": 800})
            
            await page.set_content(html)
            await page.wait_for_load_state("networkidle")
            
            # Get the full content height
            full_height = await page.evaluate("() => document.body.scrollHeight")
            await page.set_viewport_size({"width": 1200, "height": full_height})
            
            await page.screenshot(path=str(output_path), full_page=True)
            await browser.close()
            
            return True
    except Exception as e:
        print(f"[ERROR] Screenshot generation failed: {e}")
        return False


async def generate_earnings_screenshot() -> Optional[Path]:
    """
    Main function to generate earnings screenshot
    Returns: Path to the generated PNG file or None if failed
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fetch latest date
    date = fetch_latest_date()
    if not date:
        print("[ERROR] Could not fetch latest date")
        return None
    
    print(f"[INFO] Latest date: {date}")
    
    # Fetch earnings data
    items = fetch_earnings_data(date)
    if not items:
        print("[ERROR] Could not fetch earnings data")
        return None
    
    print(f"[INFO] Fetched {len(items)} items")
    
    # Generate HTML
    html = generate_html(date, items)
    
    # Generate screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"earnings_{date}_{timestamp}.png"
    
    success = await generate_screenshot(html, output_path)
    if success:
        print(f"[SUCCESS] Screenshot saved: {output_path}")
        return output_path
    else:
        print("[ERROR] Failed to generate screenshot")
        return None


def sync_generate_earnings_screenshot() -> Optional[Path]:
    """Synchronous wrapper for generating screenshot (use this in your workflow)"""
    return asyncio.run(generate_earnings_screenshot())


if __name__ == "__main__":
    import sys
    
    screenshot_path = sync_generate_earnings_screenshot()
    if screenshot_path:
        print(screenshot_path)
        sys.exit(0)
    else:
        sys.exit(1)
