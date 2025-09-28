import asyncio
from playwright.async_api import Page

async def search_jobs_simple(page: Page, job_title: str = "Product Manager", location: str = "India") -> None:
	"""Simple job search function"""
	print(f"[DEBUG] Searching for jobs: {job_title} in {location}")
	
	# Wait for page to load
	await asyncio.sleep(3)
	
	# Take screenshot before search
	await page.screenshot(path="debug_before_search.png")
	print(f"[DEBUG] Screenshot saved: debug_before_search.png")
	
	# Fill job title
	try:
		title_input = page.locator("css=input[placeholder*='Title, skill or Company']").first
		await title_input.fill(job_title)
		print(f"[DEBUG] Filled job title: {job_title}")
	except Exception as e:
		print(f"[DEBUG] Job title input failed: {e}")
		# Try alternative selectors
		try:
			title_input = page.locator("css=input[type='text']").first
			await title_input.fill(job_title)
			print(f"[DEBUG] Filled job title (alternative): {job_title}")
		except Exception as e2:
			print(f"[DEBUG] Alternative job title input failed: {e2}")
			return
	
	# Fill location
	try:
		location_input = page.locator("css=input[placeholder*='City, state, or zip code']").first
		await location_input.fill(location)
		print(f"[DEBUG] Filled location: {location}")
		
		# Wait for dropdown and select first option
		await asyncio.sleep(2)
		dropdown_option = page.locator("css=li:has-text('India')").first
		if await dropdown_option.count():
			await dropdown_option.click()
			print(f"[DEBUG] Selected 'India' from dropdown")
		else:
			# Try pressing Enter
			await location_input.press("Enter")
			print(f"[DEBUG] Pressed Enter to confirm location")
	except Exception as e:
		print(f"[DEBUG] Location input failed: {e}")
		# Try alternative approach
		try:
			location_input = page.locator("css=input[type='text']").nth(1)
			await location_input.fill(location)
			await location_input.press("Enter")
			print(f"[DEBUG] Filled location (alternative): {location}")
		except Exception as e2:
			print(f"[DEBUG] Alternative location input failed: {e2}")
	
	# Submit search - try multiple approaches
	search_success = False
	
	# Try 1: Click search button
	try:
		search_btn = page.locator("css=button:has-text('Search')").first
		await search_btn.click()
		print(f"[DEBUG] Clicked search button")
		search_success = True
	except Exception as e:
		print(f"[DEBUG] Search button failed: {e}")
	
	# Try 2: Press Enter on title input
	if not search_success:
		try:
			title_input = page.locator("css=input[placeholder*='Title, skill or Company']").first
			await title_input.press("Enter")
			print(f"[DEBUG] Pressed Enter on title input")
			search_success = True
		except Exception as e:
			print(f"[DEBUG] Enter on title input failed: {e}")
	
	# Try 3: Press Enter on location input
	if not search_success:
		try:
			location_input = page.locator("css=input[placeholder*='City, state, or zip code']").first
			await location_input.press("Enter")
			print(f"[DEBUG] Pressed Enter on location input")
			search_success = True
		except Exception as e:
			print(f"[DEBUG] Enter on location input failed: {e}")
	
	# Wait for search results to load
	if search_success:
		print(f"[DEBUG] Search submitted, waiting for results...")
		await asyncio.sleep(5)
		
		# Take screenshot after search
		await page.screenshot(path="debug_after_search.png")
		print(f"[DEBUG] Screenshot saved: debug_after_search.png")
		
		# Check if we're on the results page
		try:
			# Look for job listings or filter buttons to confirm we're on results page
			job_listings = page.locator("css=.jobs-search-results__list-item").first
			if await job_listings.count():
				print(f"[DEBUG] Found job listings - search successful!")
			else:
				print(f"[DEBUG] No job listings found - search may have failed")
		except Exception as e:
			print(f"[DEBUG] Could not verify search results: {e}")
	else:
		print(f"[DEBUG] All search methods failed")
	
	print(f"[DEBUG] Job search completed")
