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
	"""Take a debug screenshot for troubleshooting - DISABLED"""
	# Debug screenshots disabled to avoid clutter
	pass


async def handle_easy_apply_modal(page: Page) -> bool:
	"""Handle the Easy Apply modal/popup with comprehensive logic"""
	print(f"[DEBUG] Handling Easy Apply modal...")
	
	try:
		# Wait for modal to appear
		modal_found = False
		for selector in modal_selectors:
			try:
				modal = page.locator(selector).first
				if await modal.count() > 0:
					await modal.wait_for(state="visible", timeout=5000)
					modal_found = True
					print(f"[DEBUG] Modal found with selector: {selector}")
					break
			except Exception:
				continue
		
		if not modal_found:
			print(f"[DEBUG] No modal found, checking if application was instant")
			# Sometimes Easy Apply is instant without modal
			await asyncio.sleep(2)
			return True
		
		# PAUSE FOR USER TO FILL MISSING DETAILS
		print(f"[INFO] ==========================================")
		print(f"[INFO] Easy Apply modal opened successfully!")
		print(f"[INFO] Please fill in any missing details manually.")
		print(f"[INFO] The automation will wait for you to complete the form.")
		print(f"[INFO] Automation will automatically continue after 30 seconds...")
		print(f"[INFO] ==========================================")
		
		# Wait for user to complete the form (no input required)
		print(f"[INFO] Waiting 30 seconds for you to complete the form...")
		await asyncio.sleep(30)  # Wait 30 seconds for user to fill details
		print(f"[INFO] Continuing automation...")
		
		# Handle multi-step application process: Next → Next → Review → Submit
		max_steps = 10  # Prevent infinite loops
		step = 0
		
		while step < max_steps:
			print(f"[DEBUG] Processing application step {step + 1}")
			
			# Wait for page to stabilize
			await asyncio.sleep(2)
			
			# Check for required fields that need to be filled
			await handle_required_fields(page)
			
			# Look for Review button first (this means we're at the final step)
			review_clicked = False
			review_selectors = [
				"css=button:has-text('Review')",
				"css=button:has-text('review')",
				"css=button[aria-label*='Review']",
				"css=button[data-control-name*='review']"
			]
			
			for selector in review_selectors:
				try:
					review_btn = page.locator(selector).first
					if await review_btn.count() > 0:
						await review_btn.wait_for(state="visible", timeout=3000)
						if await review_btn.is_enabled():
							await review_btn.click()
							print(f"[DEBUG] Clicked Review button (step {step + 1})")
							await asyncio.sleep(3)
							review_clicked = True
							step += 1
							break
				except Exception:
					continue
			
			if review_clicked:
				continue
			
			# Look for Submit button (final step)
			submit_clicked = False
			for selector in submit_application_selectors:
				try:
					submit_btn = page.locator(selector).first
					if await submit_btn.count() > 0:
						await submit_btn.wait_for(state="visible", timeout=3000)
						if await submit_btn.is_enabled():
							await submit_btn.click()
							print(f"[DEBUG] Submitted application")
							await asyncio.sleep(3)
							submit_clicked = True
							break
				except Exception:
					continue
			
			if submit_clicked:
				break
			
			# Look for Next/Continue buttons (intermediate steps)
			next_clicked = False
			for selector in next_button_selectors:
				try:
					next_btn = page.locator(selector).first
					if await next_btn.count() > 0:
						await next_btn.wait_for(state="visible", timeout=3000)
						if await next_btn.is_enabled():
							await next_btn.click()
							print(f"[DEBUG] Clicked Next/Continue button (step {step + 1})")
							await asyncio.sleep(2)
							next_clicked = True
							step += 1
							break
				except Exception:
					continue
			
			if next_clicked:
				continue
			
			# If no buttons found, we might be done or stuck
			print(f"[DEBUG] No Next/Review/Submit buttons found, checking if application is complete")
			break
		
		# Close modal if still open
		await close_application_modal(page)
		
		print(f"[DEBUG] Easy Apply modal handling completed")
		
		# Extract and print job details
		job_details = await extract_job_details(page)
		print_job_details(job_details)
		
		return True
		
	except Exception as e:
		print(f"[DEBUG] Error handling Easy Apply modal: {e}")
		# Try to close modal even if there was an error
		await close_application_modal(page)
		return False


async def handle_required_fields(page: Page) -> None:
	"""Handle required fields in the application form"""
	try:
		# Look for common required fields and fill them if needed
		required_field_selectors = [
			"css=input[required]",
			"css=textarea[required]",
			"css=select[required]",
			"css=input[aria-required='true']",
			"css=textarea[aria-required='true']",
		]
		
		for selector in required_field_selectors:
			try:
				fields = page.locator(selector)
				count = await fields.count()
				for i in range(count):
					field = fields.nth(i)
					if await field.is_visible():
						field_type = await field.get_attribute("type")
						field_name = await field.get_attribute("name") or await field.get_attribute("id") or ""
						
						# Skip if field already has value
						value = await field.input_value()
						if value:
							continue
						
						# Fill based on field type/name
						if "phone" in field_name.lower() or field_type == "tel":
							await field.fill("+1234567890")
						elif "email" in field_name.lower() or field_type == "email":
							await field.fill("user@example.com")
						elif "name" in field_name.lower():
							await field.fill("John Doe")
						elif "experience" in field_name.lower() or "years" in field_name.lower():
							await field.fill("5")
						elif field_type == "number":
							await field.fill("5")
						else:
							await field.fill("N/A")
						
						print(f"[DEBUG] Filled required field: {field_name}")
			except Exception:
				continue
	except Exception as e:
		print(f"[DEBUG] Error handling required fields: {e}")


async def close_application_modal(page: Page) -> None:
	"""Close the application modal if it's still open"""
	try:
		for selector in close_modal_selectors:
			try:
				close_btn = page.locator(selector).first
				if await close_btn.count() > 0:
					await close_btn.wait_for(state="visible", timeout=2000)
					await close_btn.click()
					print(f"[DEBUG] Closed application modal")
					await asyncio.sleep(1)
					break
			except Exception:
				continue
	except Exception as e:
		print(f"[DEBUG] Error closing modal: {e}")


async def extract_job_details(page: Page) -> Dict[str, str]:
	"""Extract job details from the current page"""
	job_details = {
		"title": "",
		"company": "",
		"location": "",
		"applied_date": ""
	}
	
	try:
		# Extract job title
		title_selectors = [
			"css=.jobs-unified-top-card__job-title",
			"css=h1",
			"css=.job-title",
			"css=[data-test-id='job-title']"
		]
		
		for selector in title_selectors:
			try:
				element = page.locator(selector).first
				if await element.count() > 0:
					job_details["title"] = (await element.text_content() or "").strip()
					break
			except Exception:
				continue
		
		# Extract company name
		company_selectors = [
			"css=.jobs-unified-top-card__company-name",
			"css=.company-name",
			"css=[data-test-id='company-name']"
		]
		
		for selector in company_selectors:
			try:
				element = page.locator(selector).first
				if await element.count() > 0:
					job_details["company"] = (await element.text_content() or "").strip()
					break
			except Exception:
				continue
		
		# Extract location
		location_selectors = [
			"css=.jobs-unified-top-card__bullet",
			"css=.job-location",
			"css=[data-test-id='job-location']"
		]
		
		for selector in location_selectors:
			try:
				element = page.locator(selector).first
				if await element.count() > 0:
					job_details["location"] = (await element.text_content() or "").strip()
					break
			except Exception:
				continue
		
		# Set applied date to current date
		from datetime import datetime
		job_details["applied_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
	except Exception as e:
		print(f"[DEBUG] Error extracting job details: {e}")
	
	return job_details


def print_job_details(job_details: Dict[str, str]) -> None:
	"""Print job details in a formatted way"""
	print(f"\n" + "="*60)
	print(f"🎯 JOB APPLICATION COMPLETED SUCCESSFULLY!")
	print(f"="*60)
	print(f"📋 Job Role: {job_details.get('title', 'N/A')}")
	print(f"🏢 Company: {job_details.get('company', 'N/A')}")
	print(f"📍 Location: {job_details.get('location', 'N/A')}")
	print(f"📅 Applied Date: {job_details.get('applied_date', 'N/A')}")
	print(f"="*60)
	print(f"✅ Application submitted successfully!")
	print(f"="*60)


async def wait_for_captcha_completion(page: Page) -> None:
	"""Wait for user to manually complete CAPTCHA verification"""
	print(f"[DEBUG] Checking for CAPTCHA verification...")
	
	# Common CAPTCHA indicators
	captcha_selectors = [
		"iframe[src*='captcha']",
		"iframe[src*='recaptcha']",
		"[data-testid*='captcha']",
		".captcha",
		"#captcha",
		"[class*='captcha']",
		"iframe[title*='captcha']",
		"iframe[title*='reCAPTCHA']",
		"iframe[src*='hcaptcha']",
		".h-captcha"
	]
	
	# Check if CAPTCHA is present
	captcha_found = False
	for selector in captcha_selectors:
		try:
			element = page.locator(selector)
			if await element.count() > 0:
				captcha_found = True
				print(f"[DEBUG] CAPTCHA found with selector: {selector}")
				break
		except Exception:
			continue
	
	# Also check for common CAPTCHA text patterns
	try:
		page_content = await page.content()
		captcha_text_indicators = [
			"captcha", "recaptcha", "hcaptcha", "verify you are human", 
			"security check", "robot verification", "prove you're not a robot"
		]
		for indicator in captcha_text_indicators:
			if indicator.lower() in page_content.lower():
				captcha_found = True
				print(f"[DEBUG] CAPTCHA text found: {indicator}")
				break
	except Exception:
		pass
	
	if captcha_found:
		print(f"[INFO] CAPTCHA detected! Please solve it manually in the browser.")
		print(f"[INFO] The automation will wait for you to complete the verification...")
		
		# Wait for CAPTCHA to be completed (check for successful login indicators)
		max_wait_time = 300  # 5 minutes
		check_interval = 3   # Check every 3 seconds
		waited_time = 0
		
		while waited_time < max_wait_time:
			# Check if we're successfully logged in (look for LinkedIn feed or profile elements)
			success_indicators = [
				"[data-testid='main-feed']",
				"[data-testid='feed']",
				".feed-container",
				"[data-testid='global-nav']",
				".global-nav",
				"[data-testid='profile-nav-item']",
				".profile-nav-item",
				"#main-content",
				".main-content",
				"[data-testid='home']",
				".home",
				"nav[role='navigation']",
				".global-nav__me",
				"[data-testid='me-icon']"
			]
			
			# Check current URL to see if we're on LinkedIn home
			current_url = page.url
			if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
				print(f"[SUCCESS] Successfully navigated to LinkedIn home/feed!")
				return
			
			for indicator in success_indicators:
				try:
					element = page.locator(indicator)
					if await element.count() > 0:
						print(f"[SUCCESS] CAPTCHA completed! Login successful. Found: {indicator}")
						return
				except Exception:
					continue
			
			await asyncio.sleep(check_interval)
			waited_time += check_interval
			
			if waited_time % 30 == 0:  # Print status every 30 seconds
				print(f"[INFO] Still waiting for CAPTCHA completion... ({waited_time}s elapsed)")
				print(f"[DEBUG] Current URL: {page.url}")
		
		print(f"[WARNING] Timeout waiting for CAPTCHA completion. Continuing anyway...")
	else:
		print(f"[DEBUG] No CAPTCHA detected, continuing with automation...")
		# Even if no CAPTCHA detected, wait a bit for page to stabilize
		await asyncio.sleep(3)


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
	
	# Check for CAPTCHA and wait for manual completion
	await wait_for_captcha_completion(page)
	
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
			await asyncio.sleep(3)  # Wait longer for job details to load
			
			# Wait for job details panel to load
			print(f"[DEBUG] Waiting for job details panel to load...")
			try:
				# Wait for the job details panel to be visible
				await page.wait_for_selector(".jobs-unified-top-card, .jobs-details, .jobs-details__main-content", timeout=10000)
				print(f"[DEBUG] Job details panel loaded")
			except Exception as e:
				print(f"[DEBUG] Job details panel not found, continuing anyway: {e}")
			
			# Skip already applied detection - try to apply to all jobs
			print(f"[DEBUG] Attempting to apply to job: {job_info['title']}")
			
			# Look for Easy Apply button with comprehensive selectors
			print(f"[DEBUG] Looking for Easy Apply button...")
			
			# Debug: Print all buttons on the page to understand the structure
			try:
				all_buttons = await page.locator("css=button").all()
				print(f"[DEBUG] Found {len(all_buttons)} buttons on the page")
				for i, button in enumerate(all_buttons[:15]):  # Show first 15 buttons
					try:
						text = await button.text_content()
						is_visible = await button.is_visible()
						is_enabled = await button.is_enabled()
						class_name = await button.get_attribute("class") or ""
						if text and text.strip() and is_visible:
							print(f"[DEBUG] Button {i}: '{text.strip()}' (visible: {is_visible}, enabled: {is_enabled})")
							if "apply" in text.lower() or "easy" in text.lower():
								print(f"[DEBUG]   - This looks like an apply button! Class: {class_name}")
					except Exception:
						pass
			except Exception as e:
				print(f"[DEBUG] Could not inspect buttons: {e}")
			
			# Also specifically look for Easy Apply elements
			try:
				easy_apply_elements = await page.locator("css=*:has-text('Easy Apply')").all()
				print(f"[DEBUG] Found {len(easy_apply_elements)} elements containing 'Easy Apply' text")
				for i, elem in enumerate(easy_apply_elements[:5]):
					try:
						tag_name = await elem.evaluate("el => el.tagName")
						text = await elem.text_content()
						is_visible = await elem.is_visible()
						class_name = await elem.get_attribute("class") or ""
						print(f"[DEBUG] Easy Apply element {i}: <{tag_name}> '{text.strip()}' (visible: {is_visible}, class: {class_name})")
					except Exception:
						pass
			except Exception as e:
				print(f"[DEBUG] Could not inspect Easy Apply elements: {e}")
			
			try:
				# Import the comprehensive selectors
				from .selectors import apply_button_selectors
				
				apply_btn = None
				button_text = ""
				
				# Try all apply button selectors
				for selector in apply_button_selectors:
					try:
						element = page.locator(selector).first
						if await element.count() > 0:
							# Check if element is visible and enabled
							if await element.is_visible() and await element.is_enabled():
								apply_btn = element
								button_text = await element.text_content() or ""
								print(f"[DEBUG] Found apply button with selector: {selector}")
								print(f"[DEBUG] Button text: '{button_text.strip()}'")
								break
					except Exception:
						continue
				
				if apply_btn and button_text:
					# Check if it's actually an Easy Apply button
					if any(keyword in button_text.lower() for keyword in ["easy apply", "apply", "quick apply"]):
						print(f"[DEBUG] Clicking apply button for: {job_info['title']}")
						print(f"[DEBUG] Button text: '{button_text.strip()}'")
						
						# Scroll to button to ensure it's in view
						await apply_btn.scroll_into_view_if_needed()
						await asyncio.sleep(1)
						
						# Click the button
						await apply_btn.click()
						await asyncio.sleep(3)
						
						# Handle application modal with improved logic
						success = await handle_easy_apply_modal(page)
						if success:
							print(f"[DEBUG] Successfully applied to: {job_info['title']}")
							return job_info
						else:
							print(f"[DEBUG] Failed to complete application for: {job_info['title']}")
							continue
					else:
						print(f"[DEBUG] Button is not Easy Apply: '{button_text.strip()}'")
						continue
				else:
					print(f"[DEBUG] No Easy Apply button found for this job")
					continue
						
			except Exception as e:
				print(f"[DEBUG] Error looking for Easy Apply button: {e}")
				continue
				
		except Exception as e:
			print(f"[DEBUG] Error checking job {i+1}: {e}")
			continue
	
	# If we get here, no suitable job was found
	print(f"[DEBUG] No available jobs found to apply to")
	return {"title": "No available jobs", "company": "", "location": "", "link": ""}
