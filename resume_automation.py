#!/usr/bin/env python3
"""
Resume LinkedIn automation from current state
This script will open a new browser and continue from LinkedIn home
"""

import asyncio
from playwright.async_api import async_playwright
from src.automation_clean import launch_browser, navigate_to_jobs, apply_filters, find_and_apply_to_first_job
from src.report import write_excel_report
from rich import print as rprint


async def resume_automation():
    """Resume automation from LinkedIn home page"""
    
    print(f"[INFO] Starting LinkedIn automation from home page...")
    
    async with launch_browser(headless=False) as (browser, context):
        page = await context.new_page()
        
        # Navigate to LinkedIn (should redirect to home if already logged in)
        print(f"[INFO] Navigating to LinkedIn...")
        await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
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
            await page.screenshot(path="debug_error_resume.png")
            print(f"[DEBUG] Error screenshot saved: debug_error_resume.png")
            
            # Keep browser open for manual inspection
            print(f"[INFO] Keeping browser open for manual inspection...")
            print(f"[INFO] Press Enter to close browser")
            input()


if __name__ == "__main__":
    asyncio.run(resume_automation())
