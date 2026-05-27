from playwright.sync_api import sync_playwright
import os
import subprocess
import sys

def ensure_playwright_browsers():
    """
    KSP Server Initialization:
    Ensures the light, reliable Chromium compliance binary is cached on the host.
    """
    try:
        cache_dir = os.path.expanduser("~/.cache/ms-playwright")
        if not os.path.exists(cache_dir) or len(os.listdir(cache_dir)) == 0:
            print("[KSP SERVER] Deploying cloud-optimized browser dependencies...")
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            print("[KSP SERVER] Cloud browser stack active.")
    except Exception as e:
        print(f"[KSP SERVER WARNING] Binary check bypassed: {str(e)}")

def fetch_client_portal_data(login_url, username, password, target_data_selector):
    """
    KSP Enterprise Data Automation Engine (Pure Synchronous Build):
    Executes directly within the main thread to eliminate coroutine and loop conflicts.
    """
    print(f"[KSP ENGINE] Initializing background browser data retrieval pipeline...")
    
    # Ensure our execution binaries are locally available
    ensure_playwright_browsers()
    
    with sync_playwright() as p:
        try:
            # Launch with container arguments to bypass memory restrictions
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            print(f"[KSP ENGINE] Connecting to secure endpoint: {login_url}")
            page.goto(login_url, wait_until="networkidle", timeout=30000)
            
            print("[KSP ENGINE] Executing secure credentials injection...")
            page.locator("input[type='text'], input[type='email'], input[name='username']").first.fill(username)
            page.locator("input[type='password'], input[name='password']").first.fill(password)
            
            submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Login'), button:has-text('Sign In')").first
            submit_btn.click()
            
            page.wait_for_load_state("networkidle", timeout=30000)
            print("[KSP ENGINE] Authentication successful. Session active.")
            
            print("[KSP ENGINE] Parsing data matrix streams...")
            raw_element_data = page.locator(target_data_selector).inner_text(timeout=10000)
            
            return {
                "status": "SUCCESS",
                "source_endpoint": login_url,
                "extracted_payload": raw_element_data
            }
            
        except Exception as e:
            print(f"[KSP ERROR] Data retrieval pipeline failed: {str(e)}")
            return {"status": "FAILED", "error": str(e)}
            
        finally:
            print("[KSP ENGINE] Core retrieval context closed safely.")