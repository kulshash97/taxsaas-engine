import asyncio
from playwright.async_api import async_playwright
import json

async def fetch_client_portal_data(login_url, username, password, target_data_selector):
    """
    KSP Enterprise Data Automation Engine:
    Launches an optimized background browser instance configured specifically
    to bypass cloud container restrictions and extract portal matrices.
    """
    print(f"[KSP ENGINE] Initializing background browser data retrieval pipeline...")
    
    async with async_playwright() as p:
        # Launch browser with specific flags to run safely inside Streamlit Cloud's container
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
            # Navigate to the specified portal endpoint
            print(f"[KSP ENGINE] Connecting to secure endpoint: {login_url}")
            await page.goto(login_url, wait_until="networkidle", timeout=30000)
            
            # Execute automated secure authentication sequence
            print("[KSP ENGINE] Executing secure credentials injection...")
            await page.fill("input[type='text']", username)
            await page.fill("input[type='password']", password)
            
            # Click submit and await server handshake completion
            await page.click("button[type='submit']")
            await page.wait_for_load_state("networkidle", timeout=30000)
            print("[KSP ENGINE] Authentication successful. Session active.")
            
            # Extract target financial transaction matrix array
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
            # Ensure session is cleanly terminated to avoid memory leaks
            await context.close()
            await browser.close()
            print("[KSP ENGINE] Core retrieval browser context closed safely.")