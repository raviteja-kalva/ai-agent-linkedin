import asyncio
from playwright.async_api import async_playwright

async def debug_filters_automated():
    """Debug script with automated login"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Go to LinkedIn and login
        await page.goto("https://www.linkedin.com/", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # Login with your credentials
        try:
            # Click login button
            login_btn = page.locator("css=button:has-text('Sign in')").first
            await login_btn.click()
            await asyncio.sleep(2)
            
            # Fill credentials
            email_input = page.locator("css=input[name='session_key']").first
            await email_input.fill("raviteja.kalva@gmail.com")
            
            password_input = page.locator("css=input[name='session_password']").first
            await password_input.fill("your_password_here")  # You'll need to add your password
            
            # Submit login
            submit_btn = page.locator("css=button[type='submit']").first
            await submit_btn.click()
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Login failed: {e}")
            print("Please login manually and press Enter...")
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
    asyncio.run(debug_filters_automated())

