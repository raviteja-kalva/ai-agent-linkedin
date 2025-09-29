#!/usr/bin/env python3
"""
Continue LinkedIn automation from current state
This script assumes you're already logged in to LinkedIn
"""

import asyncio
from playwright.async_api import async_playwright
from src.automation_clean import navigate_to_jobs, apply_filters, find_and_apply_to_first_job
from src.report import write_excel_report
from rich import print as rprint


async def continue_from_linkedin_home():
    """Continue automation assuming we're already on LinkedIn home page"""
    
    async with async_playwright() as p:
        # Connect to existing browser session
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        
        print(f"[INFO] Connected to existing browser session")
        print(f"[INFO] Current URL: {page.url}")
        
        try:
            # Step 1: Navigate to Jobs
            print(f"[INFO] Navigating to Jobs section...")
            await navigate_to_jobs(page)
            
            # Step 2: Apply filters
            print(f"[INFO] Applying job filters...")
            await apply_filters(page)
            
            # Step 3: Apply to first job
            print(f"[INFO] Finding and applying to first job...")
            job = await find_and_apply_to_first_job(page)
            rprint(f"[bold]Applied to:[/bold] {job}")
            
            # Generate report
            report_path = write_excel_report(job)
            rprint(f"[bold green]Report:[/bold green] {report_path}")
            
        except Exception as e:
            print(f"[ERROR] Automation failed: {e}")
            # Take a debug screenshot
            await page.screenshot(path="debug_error_continue.png")
            print(f"[DEBUG] Error screenshot saved: debug_error_continue.png")
        
        # Keep browser open for manual inspection
        print(f"[INFO] Keeping browser open for manual inspection...")
        print(f"[INFO] Press Ctrl+C to close browser")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"[INFO] Closing browser...")
            await browser.close()


if __name__ == "__main__":
    asyncio.run(continue_from_linkedin_home())
