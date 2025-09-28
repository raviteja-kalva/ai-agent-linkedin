import asyncio
from typing import Dict, Optional, Tuple
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .selectors import (
	login_button_selectors,
	email_input_selectors,
	password_input_selectors,
	submit_login_selectors,
	jobs_menu_selectors,
)


async def wait_network_idle(page: Page, timeout: int = 10000) -> None:
	"""Wait for network to be idle with timeout fallback"""
	try:
		await page.wait_for_load_state("networkidle", timeout=timeout)
	except Exception:
		try:
			await page.wait_for_load_state("domcontentloaded", timeout=5000)
		except Exception:
			pass


async def debug_screenshot(page: Page, name: str) -> None:
	"""Take a debug screenshot for troubleshooting"""
	try:
		from datetime import datetime
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		filename = f"debug_{name}_{timestamp}.png"
		await page.screenshot(path=filename)
		print(f"[DEBUG] Screenshot saved: {filename}")
	except Exception as e:
		print(f"[DEBUG] Failed to take screenshot: {e}")


async def first_locator(page: Page, selectors: list[str], timeout: float = 6000):
	"""Find the first available element from a list of selectors"""
	for sel in selectors:
		loc = page.locator(sel)
		try:
			await loc.first.wait_for(state="visible", timeout=timeout)
			return loc.first
		except Exception:
			continue
	raise RuntimeError(f"Could not find element for selectors: {selectors}")


@asynccontextmanager
async def launch_browser(headless: bool = True) -> Tuple[Browser, BrowserContext]:
	"""Launch browser with appropriate settings"""
	async with async_playwright() as p:
		browser: Browser = await p.chromium.launch(
			headless=headless,
			args=[
				"--disable-geolocation",
				"--disable-notifications",
				"--disable-features=ConversionMeasurement,QuietNotificationPrompts",
			]
		)
		context = await browser.new_context(
			permissions=["geolocation"],
			geolocation={"latitude": 0, "longitude": 0},
		)
		try:
			yield browser, context
		finally:
			await context.close()
			await browser.close()


async def open_linkedin_and_login(context: BrowserContext, email: str, password: str) -> Page:
	"""Open LinkedIn and login"""
	page = await context.new_page()
	await page.goto("https://www.linkedin.com/", wait_until="domcontentloaded")
	await wait_network_idle(page)
	
	print(f"[DEBUG] Logging into LinkedIn...")
	
	# Take screenshot before login
	await debug_screenshot(page, "before_login")
	
	# Click login button if needed
	try:
		login_btn = await first_locator(page, login_button_selectors, timeout=5000)
		await login_btn.click()
		await asyncio.sleep(2)
		print(f"[DEBUG] Clicked login button")
	except Exception:
		print(f"[DEBUG] No login button found, continuing...")
	
	# Fill credentials
	print(f"[DEBUG] Filling email: {email}")
	email_input = await first_locator(page, email_input_selectors)
	await email_input.fill(email)
	
	print(f"[DEBUG] Filling password")
	password_input = await first_locator(page, password_input_selectors)
	await password_input.fill(password)
	
	# Submit login
	print(f"[DEBUG] Submitting login form")
	submit_btn = await first_locator(page, submit_login_selectors)
	await submit_btn.click()
	
	# Wait for login to complete
	await asyncio.sleep(5)
	await wait_network_idle(page)
	
	# Take screenshot after login attempt
	await debug_screenshot(page, "after_login_attempt")
	
	print(f"[DEBUG] Login process completed")
	return page


async def navigate_to_jobs(page: Page) -> None:
	"""Navigate to Jobs section"""
	print(f"[DEBUG] Navigating to Jobs section...")
	
	# Try to find Jobs link first
	try:
		jobs_link = await first_locator(page, jobs_menu_selectors, timeout=5000)
		await jobs_link.click()
		await wait_network_idle(page)
		print(f"[DEBUG] Successfully navigated to Jobs")
		
		# Now search for Product Manager in India
		print(f"[DEBUG] Searching for Product Manager jobs in India...")
		
		# Wait for page to load completely
		await asyncio.sleep(3)
		
		# Try multiple approaches to fill the search form
		search_successful = False
		
		# Approach 1: Try to find and fill job title input
		try:
			title_selectors = [
				"input[placeholder*='job title']",
				"input[placeholder*='Job title']", 
				"input[aria-label*='job title']",
				"input[placeholder*='Title, skill']",
				"input[name='keywords']"
			]
			
			for selector in title_selectors:
				try:
					title_input = page.locator(selector).first
					if await title_input.count():
						await title_input.fill("Product Manager")
						print(f"[DEBUG] Filled job title with selector: {selector}")
						search_successful = True
						break
				except Exception:
					continue
		except Exception as e:
			print(f"[DEBUG] Could not fill job title: {e}")
		
		# Approach 2: Try to find and fill location input
		try:
			location_selectors = [
				"input[placeholder*='location']",
				"input[placeholder*='Location']",
				"input[aria-label*='location']",
				"input[placeholder*='City, state']",
				"input[name='location']"
			]
			
			for selector in location_selectors:
				try:
					location_input = page.locator(selector).first
					if await location_input.count():
						await location_input.fill("India")
						print(f"[DEBUG] Filled location with selector: {selector}")
						await asyncio.sleep(1)
						break
				except Exception:
					continue
		except Exception as e:
			print(f"[DEBUG] Could not fill location: {e}")
		
		# Approach 3: Try to submit the search
		if search_successful:
			try:
				# Try pressing Enter on the location input
				location_input = page.locator("input[placeholder*='location'], input[placeholder*='Location'], input[placeholder*='City, state']").first
				if await location_input.count():
					await location_input.press("Enter")
					print(f"[DEBUG] Pressed Enter to search")
					await wait_network_idle(page)
					await asyncio.sleep(3)
					
					# Check if we're now on search results page
					current_url = page.url
					if "search" in current_url.lower() and "keywords" in current_url.lower():
						print(f"[DEBUG] Successfully navigated to search results: {current_url}")
					else:
						print(f"[DEBUG] Still on main page, trying alternative search methods...")
						# Try clicking search button
						search_btn = page.locator("button:has-text('Search'), button[aria-label*='Search']").first
						if await search_btn.count():
							await search_btn.click(force=True)
							print(f"[DEBUG] Force clicked search button")
							await wait_network_idle(page)
							await asyncio.sleep(3)
			except Exception as e:
				print(f"[DEBUG] Enter key failed: {e}")
		
		# Final fallback: Direct URL navigation to search results
		print(f"[DEBUG] Using direct URL navigation to search results...")
		try:
			search_url = "https://www.linkedin.com/jobs/search/?keywords=Product%20Manager&location=India"
			await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
			await wait_network_idle(page)
			await asyncio.sleep(3)
			print(f"[DEBUG] Direct URL navigation to search results successful")
		except Exception as e:
			print(f"[DEBUG] Direct URL navigation failed: {e}")
			
	except Exception as e:
		print(f"[DEBUG] Could not find Jobs menu: {e}")
		# Try direct navigation to jobs page
		print(f"[DEBUG] Trying direct navigation to jobs page...")
		try:
			await page.goto("https://www.linkedin.com/jobs/", wait_until="domcontentloaded", timeout=15000)
			await wait_network_idle(page)
			print(f"[DEBUG] Direct navigation to jobs page completed")
		except Exception as e2:
			print(f"[DEBUG] Direct navigation failed: {e2}")


async def apply_filters(page: Page) -> None:
	"""Apply job search filters"""
	print(f"[DEBUG] Applying filters...")
	
	# Take screenshot before applying filters
	await debug_screenshot(page, "before_filters")
	
	# Debug: Print all buttons on the page to understand the structure
	print(f"[DEBUG] Inspecting page for filter buttons...")
	try:
		all_buttons = await page.locator("css=button").all()
		print(f"[DEBUG] Found {len(all_buttons)} buttons on the page")
		for i, button in enumerate(all_buttons[:15]):  # Show first 15 buttons
			try:
				text = await button.text_content()
				if text and text.strip():
					print(f"[DEBUG] Button {i}: '{text.strip()}'")
			except Exception:
				pass
	except Exception as e:
		print(f"[DEBUG] Could not inspect buttons: {e}")
	
	# Step 1: Apply Date Posted filter - "Past 24 hours"
	print(f"[DEBUG] Step 1: Applying Date Posted filter...")
	try:
		# Look for Date posted button with multiple selectors
		date_filter_selectors = [
			"css=button:has-text('Date posted')",
			"css=button:has-text('Date')",
			"css=button[aria-label*='Date posted']",
			"css=button[data-test-id*='date-posted']",
			"css=.jobs-search-date-posted-filter",
		]
		
		date_filter = None
		for selector in date_filter_selectors:
			try:
				element = page.locator(selector).first
				if await element.count() > 0:
					date_filter = element
					print(f"[DEBUG] Found Date posted button with selector: {selector}")
					break
			except Exception:
				continue
		
		if date_filter:
			await date_filter.click()
			await asyncio.sleep(2)
			print(f"[DEBUG] Clicked Date Posted filter")
			
			# Select "Past 24 hours" radio button
			past_24_selectors = [
				"css=input[type='radio'][value*='24']",
				"css=label:has-text('Past 24 hours')",
				"css=li:has-text('Past 24 hours')",
				"css=*:has-text('Past 24 hours')",
				"css=button:has-text('Past 24 hours')",
			]
			
			selected = False
			for selector in past_24_selectors:
				try:
					option = page.locator(selector).first
					if await option.count() > 0:
						await option.click()
						print(f"[DEBUG] Selected 'Past 24 hours' with selector: {selector}")
						await asyncio.sleep(1)
						selected = True
						break
				except Exception:
					continue
			
			if not selected:
				print(f"[DEBUG] Could not find 'Past 24 hours' option")
			
			# Click the "Show X+ results" button (this is the key step!)
			print(f"[DEBUG] Looking for 'Show X+ results' button...")
			show_results_selectors = [
				"css=button:has-text('Show')",
				"css=button:has-text('results')",
				"css=button:has-text('Show results')",
				"css=button:has-text('Show Results')",
				"css=button[type='submit']",
				"css=button[aria-label*='Show results']",
			]
			
			show_clicked = False
			for selector in show_results_selectors:
				try:
					btn = page.locator(selector).first
					if await btn.count() > 0:
						button_text = await btn.text_content()
						print(f"[DEBUG] Found button: '{button_text}' with selector: {selector}")
						await btn.click()
						await wait_network_idle(page)
						await asyncio.sleep(3)
						print(f"[DEBUG] Clicked Show Results button")
						show_clicked = True
						break
				except Exception:
					continue
			
			if not show_clicked:
				print(f"[DEBUG] Could not find Show Results button")
		else:
			print(f"[DEBUG] Could not find Date posted filter button")
			
	except Exception as e:
		print(f"[DEBUG] Date filter failed: {e}")
	
	# Step 2: Apply Easy Apply filter
	print(f"[DEBUG] Step 2: Applying Easy Apply filter...")
	try:
		easy_apply_selectors = [
			"css=button:has-text('Easy Apply')",
			"css=input[type='checkbox']:near(text='Easy Apply')",
			"css=label:has-text('Easy Apply')",
			"css=button[aria-label*='Easy Apply']",
		]
		
		easy_apply = None
		for selector in easy_apply_selectors:
			try:
				element = page.locator(selector).first
				if await element.count() > 0:
					easy_apply = element
					print(f"[DEBUG] Found Easy Apply button with selector: {selector}")
					break
			except Exception:
				continue
		
		if easy_apply:
			await easy_apply.click()
			await asyncio.sleep(2)
			print(f"[DEBUG] Applied Easy Apply filter")
		else:
			print(f"[DEBUG] Could not find Easy Apply filter button")
			
	except Exception as e:
		print(f"[DEBUG] Easy Apply filter failed: {e}")
	
	# Take screenshot after applying filters
	await debug_screenshot(page, "after_filters")


async def find_and_apply_to_first_job(page: Page) -> Dict[str, str]:
	"""Find the first available job and apply to it"""
	print(f"[DEBUG] Looking for first available job to apply...")
	
	# Wait for job listings to load
	await wait_network_idle(page)
	await asyncio.sleep(3)
	
	# Take screenshot to see job listings
	await debug_screenshot(page, "job_listings")
	
	# Get all job cards
	job_cards = page.locator(".jobs-search-results__list-item, .job-card-container, [data-job-id]")
	job_count = await job_cards.count()
	print(f"[DEBUG] Found {job_count} job cards")
	
	# Try each job card until we find one we can apply to
	for i in range(min(job_count, 10)):  # Limit to first 10 jobs
		try:
			print(f"[DEBUG] Checking job {i+1}/{min(job_count, 10)}")
			
			# Get the current job card
			job_card = job_cards.nth(i)
			
			# Extract job information
			job_info = {
				"title": "",
				"company": "",
				"location": "",
				"link": "",
			}
			
			# Get job title
			try:
				title_elem = job_card.locator("css=h3, css=.job-card-list__title, css=a[data-control-name='job_card_click']").first
				job_info["title"] = (await title_elem.text_content() or "").strip()
			except Exception:
				pass
			
			# Get company name
			try:
				company_elem = job_card.locator("css=.job-card-container__company-name, css=.job-card-list__company-name").first
				job_info["company"] = (await company_elem.text_content() or "").strip()
			except Exception:
				pass
			
			# Get location
			try:
				location_elem = job_card.locator("css=.job-card-container__metadata-item, css=.job-card-list__metadata-item").first
				job_info["location"] = (await location_elem.text_content() or "").strip()
			except Exception:
				pass
			
			print(f"[DEBUG] Checking job: {job_info['title']} at {job_info['company']}")
			
			# Click on the job to open it
			await job_card.click()
			await wait_network_idle(page)
			await asyncio.sleep(2)
			
			# Check if job is already applied to
			applied_indicators = [
				"css=*:has-text('Applied')",
				"css=*:has-text('Application sent')",
				"css=*:has-text('See application')",
				"css=.jobs-apply-button:has-text('Applied')",
				"css=button:has-text('Applied')"
			]
			
			already_applied = False
			for indicator in applied_indicators:
				if await page.locator(indicator).count() > 0:
					already_applied = True
					print(f"[DEBUG] Job already applied to: {job_info['title']}")
					break
			
			if already_applied:
				print(f"[DEBUG] Skipping already applied job, trying next...")
				continue
			
			# Look for Easy Apply button
			print(f"[DEBUG] Looking for Easy Apply button...")
			try:
				apply_btn = page.locator("css=button:has-text('Easy Apply'), css=button:has-text('Apply'), css=.jobs-apply-button").first
				if await apply_btn.count():
					button_text = await apply_btn.text_content()
					print(f"[DEBUG] Found apply button: {button_text}")
					
					# Check if it's actually an Easy Apply button
					if "Easy Apply" in button_text or "Apply" in button_text:
						print(f"[DEBUG] Clicking apply button for: {job_info['title']}")
						await apply_btn.click()
						await asyncio.sleep(2)
						
						# Handle application modal
						try:
							# Look for Next/Continue buttons
							next_btn = page.locator("css=button:has-text('Next'), css=button:has-text('Continue')").first
							if await next_btn.count():
								await next_btn.click()
								print(f"[DEBUG] Clicked Next in application")
								await asyncio.sleep(1)
							
							# Look for Submit button
							submit_btn = page.locator("css=button:has-text('Submit'), css=button:has-text('Submit application')").first
							if await submit_btn.count():
								await submit_btn.click()
								print(f"[DEBUG] Submitted application")
								await asyncio.sleep(2)
							
							# Close modal if still open
							close_btn = page.locator("css=button[aria-label='Dismiss'], css=button:has-text('×')").first
							if await close_btn.count():
								await close_btn.click()
								print(f"[DEBUG] Closed application modal")
						except Exception as e:
							print(f"[DEBUG] Application modal handling failed: {e}")
						
						print(f"[DEBUG] Successfully applied to: {job_info['title']}")
						return job_info
					else:
						print(f"[DEBUG] Button is not Easy Apply: {button_text}")
						continue
						
			except Exception as e:
				print(f"[DEBUG] No Easy Apply button found for this job: {e}")
				continue
				
		except Exception as e:
			print(f"[DEBUG] Error checking job {i+1}: {e}")
			continue
	
	# If we get here, no suitable job was found
	print(f"[DEBUG] No available jobs found to apply to")
	return {"title": "No available jobs", "company": "", "location": "", "link": ""}
