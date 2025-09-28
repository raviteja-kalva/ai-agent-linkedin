import asyncio
from playwright.async_api import async_playwright

async def debug_filters_with_login():
    """Debug script to inspect the LinkedIn filters page after login"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Go to LinkedIn and login
        await page.goto("https://www.linkedin.com/", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # Login (you'll need to do this manually or use your credentials)
        print("Please login to LinkedIn manually, then press Enter to continue...")
        input("Press Enter after logging in...")
        
        # Navigate to jobs
        await page.goto("https://www.linkedin.com/jobs/", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Search for jobs
        try:
            title_input = page.locator("css=input[placeholder*='Title, skill or Company']").first
            await title_input.fill("Product Manager")
            
            location_input = page.locator("css=input[placeholder*='City, state, or zip code']").first
            await location_input.fill("India")
            await location_input.press("Enter")
            
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Search failed: {e}")
        
        print("=== DEBUGGING LINKEDIN FILTERS ===")
        
        # Take a screenshot
        await page.screenshot(path="debug_linkedin_jobs_page.png")
        print("Screenshot saved: debug_linkedin_jobs_page.png")
        
        # Look for all buttons
        print("\n=== All button texts ===")
        buttons = await page.locator("css=button").all()
        for i, button in enumerate(buttons):
            try:
                text = await button.text_content()
                if text and text.strip():
                    print(f"Button {i}: '{text.strip()}'")
            except Exception:
                pass
        
        # Look specifically for filter buttons
        print("\n=== Looking for filter-related buttons ===")
        filter_keywords = ["date", "easy", "all", "filter", "sort", "recent"]
        for keyword in filter_keywords:
            print(f"\n--- Buttons containing '{keyword}' ---")
            for i, button in enumerate(buttons):
                try:
                    text = await button.text_content()
                    if text and keyword.lower() in text.lower():
                        print(f"Button {i}: '{text.strip()}'")
                except Exception:
                    pass
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_filters_with_login())

