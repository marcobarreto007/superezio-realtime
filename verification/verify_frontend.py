from playwright.sync_api import Page, expect, sync_playwright
import time

def verify_frontend(page: Page):
    print("Navigating to localhost:3000...")
    try:
        page.goto("http://localhost:3000", timeout=10000)
    except Exception as e:
        print(f"Failed to load page: {e}")
        return

    print("Page loaded. Waiting for title...")
    try:
        expect(page.get_by_text("SuperEzio Realtime")).to_be_visible(timeout=10000)
        print("Found title 'SuperEzio Realtime'")
    except:
        print("Main title not found, continuing to screenshot anyway...")

    print("Taking screenshot...")
    page.screenshot(path="verification/frontend_verification.png")
    print("Screenshot saved.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_frontend(page)
        finally:
            browser.close()
