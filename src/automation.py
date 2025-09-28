import asyncio
from typing import Dict, Optional, Tuple
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .search_simple import search_jobs_simple
from .selectors import (
	login_button_selectors,
	email_input_selectors,
	password_input_selectors,
	submit_login_selectors,
	jobs_menu_selectors,
	job_title_input_selectors,
	location_input_selectors,
	search_button_selectors,
	date_posted_filter_selectors,
	date_posted_options,
	easy_apply_filter_selectors,
	all_filters_selectors,
	sort_dropdown_selectors,
	sort_options,
	show_results_selectors,
	job_card_selectors,
	job_title_selectors,
	company_name_selectors,
	location_selectors,
	apply_button_selectors,
	modal_selectors,
	next_button_selectors,
	submit_application_selectors,
	close_modal_selectors,
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
	
	# Check if login was successful by looking for profile elements or jobs page
	try:
		# Look for profile indicator or jobs page elements
		profile_indicator = page.locator("css=[data-test-id='profile-nav-item'], css=.global-nav__me, css=a[href*='/in/']").first
		if await profile_indicator.count():
			print(f"[DEBUG] Login successful - profile found")
		else:
			# Check if we're on jobs page
			current_url = page.url
			if "jobs" in current_url.lower() or "feed" in current_url.lower():
				print(f"[DEBUG] Login successful - redirected to: {current_url}")
			else:
				print(f"[DEBUG] Login may have failed - current URL: {current_url}")
				await debug_screenshot(page, "login_failed")
	except Exception as e:
		print(f"[DEBUG] Could not verify login status: {e}")
	
	print(f"[DEBUG] Login process completed")
	return page


async def navigate_to_jobs(page: Page) -> None:
	"""Navigate to Jobs section"""
	print(f"[DEBUG] Navigating to Jobs section...")
	
	jobs_link = await first_locator(page, jobs_menu_selectors)
	await jobs_link.click()
	await wait_network_idle(page)
	
	print(f"[DEBUG] Successfully navigated to Jobs")


async def search_jobs(page: Page, job_title: str = "Product Manager", location: str = "India") -> None:
	"""Search for jobs with title and location"""
	print(f"[DEBUG] Searching for jobs: {job_title} in {location}")
	
	# Take screenshot to see current page state
	await debug_screenshot(page, "before_job_search")
	
	# Wait a bit for page to fully load
	await asyncio.sleep(3)
	
	# Try to find job title input with more debugging
	print(f"[DEBUG] Looking for job title input...")
	try:
		title_input = await first_locator(page, job_title_input_selectors)
		print(f"[DEBUG] Found job title input")
		await title_input.fill(job_title)
		print(f"[DEBUG] Filled job title: {job_title}")
	except Exception as e:
		print(f"[DEBUG] Could not find job title input: {e}")
		await debug_screenshot(page, "no_job_title_input")
		# Try alternative approach - look for any input field
		try:
			any_input = page.locator("css=input[type='text']").first
			if await any_input.count():
				print(f"[DEBUG] Found generic input, trying to use it")
				await any_input.fill(job_title)
			else:
				print(f"[DEBUG] No input fields found at all")
			return
		except Exception as e2:
			print(f"[DEBUG] Alternative approach failed: {e2}")
			return
	
	# Try to find location input
	print(f"[DEBUG] Looking for location input...")
	try:
		location_input = await first_locator(page, location_input_selectors)
		print(f"[DEBUG] Found location input")
		await location_input.fill(location)
		print(f"[DEBUG] Filled location: {location}")
		
		# Wait for dropdown to appear and select the first option
		await asyncio.sleep(2)
		print(f"[DEBUG] Looking for location dropdown options...")
		
		# Try to click on the first dropdown option (usually the exact match)
		try:
			dropdown_option = page.locator("css=li:has-text('India'), css=.jobs-search-box__typeahead-suggestion:has-text('India'), css=[data-test-id='jobs-search-box-location-typeahead-suggestion']").first
			if await dropdown_option.count():
				await dropdown_option.click()
				print(f"[DEBUG] Selected 'India' from dropdown")
			else:
				# Try alternative selectors for dropdown
				alt_option = page.locator("css=li:first-child, css=.jobs-search-box__typeahead-suggestion:first-child").first
				if await alt_option.count():
					await alt_option.click()
					print(f"[DEBUG] Selected first dropdown option")
		except Exception as e:
			print(f"[DEBUG] Could not select from dropdown: {e}")
			# Try pressing Enter to confirm the location
			try:
				await location_input.press("Enter")
				print(f"[DEBUG] Pressed Enter to confirm location")
			except Exception as e2:
				print(f"[DEBUG] Enter key failed: {e2}")
		
	except Exception as e:
		print(f"[DEBUG] Could not find location input: {e}")
		# Try to find second input field
		try:
			second_input = page.locator("css=input[type='text']").nth(1)
			if await second_input.count():
				print(f"[DEBUG] Using second input for location")
				await second_input.fill(location)
				await asyncio.sleep(2)
				# Try to select from dropdown
				try:
					dropdown_option = page.locator("css=li:has-text('India')").first
					if await dropdown_option.count():
						await dropdown_option.click()
						print(f"[DEBUG] Selected 'India' from dropdown")
				except Exception as e2:
					print(f"[DEBUG] Dropdown selection failed: {e2}")
		except Exception as e2:
			print(f"[DEBUG] Could not find second input: {e2}")
	
	# Try to submit search
	print(f"[DEBUG] Looking for search button...")
	try:
		search_btn = await first_locator(page, search_button_selectors)
		print(f"[DEBUG] Found search button")
		await search_btn.click()
		print(f"[DEBUG] Clicked search button")
	except Exception as e:
		print(f"[DEBUG] Could not find search button: {e}")
		# Try pressing Enter on the input
		try:
			title_input = page.locator("css=input[type='text']").first
			await title_input.press("Enter")
			print(f"[DEBUG] Pressed Enter on input")
		except Exception as e2:
			print(f"[DEBUG] Enter key approach failed: {e2}")
	
	await wait_network_idle(page)
	print(f"[DEBUG] Job search completed")


async def apply_filters(page: Page) -> None:
	"""Apply job search filters"""
	print(f"[DEBUG] Applying filters...")
	
	# Take screenshot before applying filters
	await debug_screenshot(page, "before_filters")
	
	# Step 1: Apply Date Posted filter - "Past 24 hours"
	try:
		print(f"[DEBUG] Step 1: Applying Date Posted filter...")
		date_filter = await first_locator(page, date_posted_filter_selectors, timeout=5000)
		await date_filter.click()
		await asyncio.sleep(2)
		print(f"[DEBUG] Clicked Date Posted filter")
		
		# Select "Past 24 hours" radio button
		for option in date_posted_options:
			try:
				option_elem = page.locator(option).first
				if await option_elem.count():
					await option_elem.click()
					print(f"[DEBUG] Selected date filter: {option}")
					await asyncio.sleep(1)
					break
			except Exception:
				continue
		
		# Click the "Show X+ results" button (this is the key step!)
		try:
			print(f"[DEBUG] Looking for 'Show X+ results' button...")
			# Look for button with pattern "Show X+ results" where X can be any number
			show_results_btn = page.locator("css=button:has-text('Show'), css=button:has-text('results')").first
			if await show_results_btn.count():
				button_text = await show_results_btn.text_content()
				print(f"[DEBUG] Found button: {button_text}")
				await show_results_btn.click()
				await wait_network_idle(page)
				await asyncio.sleep(3)
				print(f"[DEBUG] Clicked Show Results button")
			else:
				# Try alternative selectors
				alt_btn = page.locator("css=button:has-text('Show'), css=button[type='submit']").first
				if await alt_btn.count():
					await alt_btn.click()
					await wait_network_idle(page)
					await asyncio.sleep(3)
					print(f"[DEBUG] Clicked alternative Show Results button")
		except Exception as e:
			print(f"[DEBUG] Show Results button not found: {e}")
			
	except Exception as e:
		print(f"[DEBUG] Date filter failed: {e}")
	
	# Step 2: Apply Easy Apply filter
	try:
		print(f"[DEBUG] Step 2: Applying Easy Apply filter...")
		easy_apply = await first_locator(page, easy_apply_filter_selectors, timeout=5000)
		await easy_apply.click()
		await asyncio.sleep(2)
		print(f"[DEBUG] Applied Easy Apply filter")
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
	
	# Get all job cards
	job_cards = page.locator("css=.jobs-search-results__list-item, css=.job-card-container, css=[data-job-id]")
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
			title_elem = job_card.locator("css=h3, css=a").first
			job_info["title"] = (await title_elem.text_content() or "").strip()
			
			# Get company name
			company_elem = job_card.locator("css=.job-card-container__company-name, css=.jobs-unified-top-card__company-name").first
			job_info["company"] = (await company_elem.text_content() or "").strip()
			
			# Get location
			location_elem = job_card.locator("css=.job-card-container__metadata-item, css=.jobs-unified-top-card__bullet").first
			job_info["location"] = (await location_elem.text_content() or "").strip()
			
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
				apply_btn = await first_locator(page, apply_button_selectors, timeout=5000)
				button_text = await apply_btn.text_content()
				print(f"[DEBUG] Found apply button: {button_text}")
				
				# Check if it's actually an Easy Apply button
				if "Easy Apply" in button_text or "Apply" in button_text:
					print(f"[DEBUG] Clicking apply button for: {job_info['title']}")
					await apply_btn.click()
					await asyncio.sleep(2)
					
					# Handle application modal
					await handle_application_modal(page)
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


async def handle_application_modal(page: Page) -> None:
	"""Handle the job application modal/overlay"""
	print(f"[DEBUG] Handling application modal...")
	
	try:
		# Wait for modal to appear
		modal = await first_locator(page, modal_selectors, timeout=10000)
		
		# Look for Next/Continue buttons and click through the application
		max_steps = 5  # Prevent infinite loops
		step = 0
		
		while step < max_steps:
			# Look for Next button
			next_btn = page.locator("css=button:has-text('Next'), css=button:has-text('Continue')").first
			if await next_btn.count():
				await next_btn.click()
				await asyncio.sleep(2)
				step += 1
				print(f"[DEBUG] Clicked Next/Continue (step {step})")
				continue
			
			# Look for Submit button
			submit_btn = page.locator("css=button:has-text('Submit'), css=button:has-text('Submit application')").first
			if await submit_btn.count():
				await submit_btn.click()
				print(f"[DEBUG] Submitted application")
				break
			
			# If no buttons found, break
			break
		
		# Close modal if still open
		try:
			close_btn = page.locator("css=button[aria-label='Dismiss'], css=button:has-text('×')").first
			if await close_btn.count():
				await close_btn.click()
				print(f"[DEBUG] Closed application modal")
	except Exception:
		pass

	except Exception as e:
		print(f"[DEBUG] Error handling application modal: {e}")
		await debug_screenshot(page, "modal_error")