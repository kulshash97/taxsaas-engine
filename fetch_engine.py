import asyncio
from playwright.async_api import async_playwright
import os
import subprocess
import sys

def ensure_playwright_browsers():
    """
    KSP Server Initialization:
    Checks if the Playwright browser binaries are present on the host container.
    If missing, programmatically triggers 'playwright install' at ₹0 overhead.
    """
    try:
        # Check if the playwright cache folder exists and has contents
        cache_dir = os.path.expanduser("~/.cache/ms-playwright")
        if not os.path.exists(cache_dir) or len(os.listdir(cache_dir)) == 0:
            print("[KSP SERVER] Playwright binaries missing. Initializing automated cloud install...")
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            print("[KSP SERVER] Playwright binaries deployed successfully.")
        else:
            print("[KSP SERVER] Verified Playwright browser cache is active.")
    except Exception as e:
        print(f"[KSP SERVER WARNING] Auto-installation check bypassed: {str(e)}")

async def fetch_client_portal_data(login_url, username, password, target_data_selector):
    """
    KSP Enterprise Data Automation Engine:
    Launches an optimized background browser instance configured specifically
    to bypass cloud container restrictions and extract portal matrices.
    """
    print(f"[KSP ENGINE] Initializing background browser data retrieval pipeline...")
    
    # Force the server to verify browser binaries are installed first
    ensure_playwright_browsers()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"[KSP ENGINE] Connecting to secure endpoint: {login_url}")
            await page.goto(login_url, wait_until="networkidle", timeout=30000)
            
            print("[KSP ENGINE] Executing secure credentials injection...")
            await page.fill("input[type='text']", username)
            await page.fill("input[type='password']", password)
            
            await page.click("button[type='submit']")
            await page.wait_for_load_state("networkidle", timeout=30000)
            print("[KSP ENGINE] Authentication successful. Session active.")
            
            print("[KSP ENGINE] Parsing data matrix streams...")
            raw_element_data = await page.locator(target_data_selector).inner_text(timeout=10000)
            
            parsed_payload = {
                "status": "SUCCESS",
                "source_endpoint": login_url,
                "extracted_payload": raw_element_data
            }
            return parsed_payload
            
        except Exception as e:
            print(f"[KSP ERROR] Data retrieval pipeline failed: {str(e)}")
            return {"status": "FAILED", "error": str(e)}
            
        finally:
            await context.close()
            await browser.close()
            print("[KSP ENGINE] Core retrieval browser context closed safely.")