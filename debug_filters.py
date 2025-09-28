import asyncio
from playwright.async_api import async_playwright

async def debug_filters():
    """Debug script to inspect the LinkedIn filters page"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Go to LinkedIn jobs page
        await page.goto("https://www.linkedin.com/jobs/", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        print("=== DEBUGGING LINKEDIN FILTERS ===")
        
        # Take a screenshot
        await page.screenshot(path="debug_linkedin_page.png")
        print("Screenshot saved: debug_linkedin_page.png")
        
        # Look for all buttons with "Date" in the text
        print("\n=== Looking for Date-related buttons ===")
        date_buttons = await page.locator("css=button").all()
        for i, button in enumerate(date_buttons):
            try:
                text = await button.text_content()
                if text and "date" in text.lower():
                    print(f"Button {i}: '{text.strip()}'")
            except Exception:
                pass
        
        # Look for all buttons with "Easy" in the text
        print("\n=== Looking for Easy Apply buttons ===")
        easy_buttons = await page.locator("css=button").all()
        for i, button in enumerate(easy_buttons):
            try:
                text = await button.text_content()
                if text and "easy" in text.lower():
                    print(f"Button {i}: '{text.strip()}'")
            except Exception:
                pass
        
        # Look for all buttons with "All" in the text
        print("\n=== Looking for All Filters buttons ===")
        all_buttons = await page.locator("css=button").all()
        for i, button in enumerate(all_buttons):
            try:
                text = await button.text_content()
                if text and "all" in text.lower():
                    print(f"Button {i}: '{text.strip()}'")
            except Exception:
                pass
        
        print("\n=== All button texts (first 20) ===")
        for i, button in enumerate(date_buttons[:20]):
            try:
                text = await button.text_content()
                if text and text.strip():
                    print(f"Button {i}: '{text.strip()}'")
            except Exception:
                pass
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_filters())

