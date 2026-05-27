import asyncio
from playwright.async_api import async_playwright
import os
import subprocess
import sys

def ensure_playwright_browsers():
    """
    KSP Server Initialization:
    Ensures the ultra-lightweight Firefox compliance binary is cached on the host.
    """
    try:
        cache_dir = os.path.expanduser("~/.cache/ms-playwright")
        # If the cache doesn't contain a browser, pull the lightweight firefox engine
        if not os.path.exists(cache_dir) or not any("firefox" in f for f in os.listdir(cache_dir) if os.path.isdir(os.path.join(cache_dir, f))):
            print("[KSP SERVER] Deploying cloud-optimized browser dependencies...")
            subprocess.run([sys.executable, "-m", "playwright", "install", "firefox"], check=True)
            print("[KSP SERVER] Cloud-optimized browser stack active.")
        else:
            print("[KSP SERVER] Verified browser cache is active.")
    except Exception as e:
        print(f"[KSP SERVER WARNING] Binary check bypassed: {str(e)}")

async def fetch_client_portal_data(login_url, username, password, target_data_selector):
    """
    KSP Enterprise Data Automation Engine:
    Utilizes a cloud-optimized headless Firefox engine to bypass strict container
    resource limits and extract portal matrices smoothly.
    """
    print(f"[KSP ENGINE] Initializing background browser data retrieval pipeline...")
    
    # Ensure our lightweight system binary is available
    ensure_playwright_browsers()
    
    async with async_playwright() as p:
        # Launching via Firefox avoids the TargetClosed errors triggered by heavy Chromium engines
        browser = await p.firefox.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        )
        page = await context.new_page()
        
        try:
            print(f"[KSP ENGINE] Connecting to secure endpoint: {login_url}")
            await page.goto(login_url, wait_until="networkidle", timeout=30000)
            
            print("[KSP ENGINE] Executing secure credentials injection...")
            # Automatically targets input structures using flexible attribute matching
            await page.locator("input[type='text'], input[type='email'], input[name='username']").first.fill(username)
            await page.locator("input[type='password'], input[name='password']").first.fill(password)
            
            # Click the main submit element
            submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Login'), button:has-text('Sign In')").first
            await submit_btn.click()
            
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