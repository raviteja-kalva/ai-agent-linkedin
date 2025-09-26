import asyncio
from typing import Dict, Optional, Tuple
from contextlib import asynccontextmanager
from urllib.parse import urljoin
import re
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .selectors import (
	login_button_selectors,
	email_input_selectors,
	password_input_selectors,
	submit_login_selectors,
	search_role_input,
	location_filter_selectors,
	department_filter_selectors,
	freshness_filter_selectors,
	apply_button_selectors,
	first_job_card_selectors,
	job_link_selectors,
	search_submit_selectors,
)


async def wait_network_idle(page: Page) -> None:
	await page.wait_for_load_state("networkidle")


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
	async with async_playwright() as p:
		# Disable geolocation/notification prompts at the browser level
		browser: Browser = await p.chromium.launch(
			headless=headless,
			args=[
				"--disable-geolocation",
				"--disable-notifications",
				"--disable-features=ConversionMeasurement,QuietNotificationPrompts",
			]
		)
		# Grant geolocation to suppress the Chrome permission bubble entirely
		context = await browser.new_context(
			permissions=["geolocation"],
			geolocation={"latitude": 0, "longitude": 0},
		)
		try:
			yield browser, context
		finally:
			await context.close()
			await browser.close()


async def open_url(context: BrowserContext, url: str) -> Page:
	page = await context.new_page()
	await page.goto(url, wait_until="domcontentloaded")
	await wait_network_idle(page)
	return page


async def open_home_and_login(context: BrowserContext, email: str, password: str) -> Page:
	page = await open_url(context, "https://www.naukri.com/")
	# Best-effort: dismiss any geolocation prompt if it appears
	await dismiss_geolocation_prompt(page)
	await login_naukri(page, email, password)
	return page


async def login_naukri(page: Page, email: str, password: str) -> None:
	# Some sessions land already logged-in; try to locate login button
	try:
		btn = await first_locator(page, login_button_selectors, timeout=5000)
		await btn.click()
	except Exception:
		pass

	# Fill credentials
	email_input = await first_locator(page, email_input_selectors)
	await email_input.fill(email)
	pwd_input = await first_locator(page, password_input_selectors)
	await pwd_input.fill(password)

	submit_btn = await first_locator(page, submit_login_selectors)
	await submit_btn.click()
	await wait_network_idle(page)


async def search_jobs(page: Page, query: str = "Product Manager") -> None:
	# Open the top search bar if collapsed
	await dismiss_geolocation_prompt(page)
	try:
		trigger = page.get_by_text("search jobs here", exact=False)
		await trigger.first.wait_for(state="visible", timeout=4000)
		await trigger.first.click()
	except Exception:
		pass

	# Fill the keyword field without clicking to avoid overlay intercepts
	try:
		kw = page.get_by_placeholder("Enter keyword", exact=False)
		await kw.first.wait_for(state="visible", timeout=6000)
		await kw.first.fill(query)
	except Exception:
		# Fallback to broader input selectors
		role_input = await first_locator(page, search_role_input, timeout=8000)
		await role_input.fill(query)

	# Submit: prefer the search icon button
	try:
		icon_btn = page.locator("css=button.nI-gNb-sb__icon-wrapper").first
		await icon_btn.wait_for(state="visible", timeout=3000)
		await icon_btn.click()
	except Exception:
		# Fallback: press Enter on the input
		try:
			kw = page.get_by_placeholder("Enter keyword", exact=False)
			await kw.first.press("Enter")
		except Exception:
			pass

	# Wait for result list to appear/refreshed
	try:
		await page.locator("css=[data-job-id], css=.list, css=.jobTuple").first.wait_for(state="visible", timeout=8000)
	except Exception:
		pass
	await dismiss_geolocation_prompt(page)


async def dismiss_geolocation_prompt(page: Page) -> None:
	"""Closes site/browser geolocation prompts if visible.

	Tries common button texts: Never allow, Block, Not now, Deny, Close (×).
	Silently ignores if not present.
	"""
	try:
		# Try site-level modal texts first (as shown in screenshot)
		for name in [
			re.compile(r"^\s*Never allow\s*$", re.I),
			re.compile(r"^\s*Block\s*$", re.I),
			re.compile(r"^\s*Not now\s*$", re.I),
			re.compile(r"^\s*Deny\s*$", re.I),
			re.compile(r"^\s*Never\s*allow\s*", re.I),
			re.compile(r"^\s*Don'?t allow\s*$", re.I),
		]:
			btn = page.get_by_role("button", name=name).first
			if await btn.count():
				await btn.click(timeout=1000)
				return
			# Try text-based locator if role lookup fails
			btn2 = page.get_by_text(name).first
			if await btn2.count():
				await btn2.click(timeout=1000)
				return
		# Try the close icon in the prompt container (top-right ×)
		close_btn = page.locator("css=button:has-text('×'), css=button:has-text('x'), css=button[aria-label*='close' i]").first
		if await close_btn.count():
			await close_btn.click(timeout=1000)
			return
		# Focus on the geolocation dialog container if present
		dialog = page.get_by_role("dialog", name=re.compile(r"know your location|wants to|location", re.I)).first
		if await dialog.count():
			try:
				await dialog.get_by_role("button", name=re.compile(r"^\s*(Close|Dismiss|Cancel|Never allow|Block|Not now|Deny)\s*$", re.I)).first.click(timeout=1000)
				return
			except Exception:
				pass
		# As a generic fallback, click any visible element with the exact text
		for t in ["Never allow", "Block", "Not now", "Deny"]:
			try:
				el = page.get_by_text(re.compile(rf"^\s*{re.escape(t)}\s*$", re.I)).first
				if await el.count():
					await el.click(timeout=800)
					return
			except Exception:
				continue
	except Exception:
		pass


async def apply_left_nav_filters(page: Page) -> None:
	# Helpers to find a section container by its heading text
	def section_container_xpath(name: str) -> str:
		return (
			"xpath=(//div[.//text()[normalize-space()=" + repr(name) + "] or .//span[normalize-space()=" + repr(name) + "] or .//h3[normalize-space()=" + repr(name) + "]])[1]"
		)

	async def open_view_more_in_section(section_name: str):
		container = page.locator(section_container_xpath(section_name)).first
		await container.scroll_into_view_if_needed()
		# Support multiple phrasings for the expander button
		for text_pattern in [
			r"^\s*View More\s*$",
			r"^\s*View more\s*$",
			r"^\s*View all\s*$",
			r"^\s*Show more\s*$",
		]:
			try:
				vm = container.get_by_text(re.compile(text_pattern, re.I))
				await vm.first.click(timeout=2000)
				break
			except Exception:
				continue
		return container

	async def robust_check_checkbox(scope, name_pattern: str) -> None:
		"""Ensure a checkbox with given accessible name is selected.

		Attempts: role-based check(), clicking label, JS-setting input.checked.
		"""
		# 1) ARIA role path
		try:
			cb = scope.get_by_role("checkbox", name=re.compile(name_pattern, re.I)).first
			await cb.wait_for(state="attached", timeout=5000)
			await cb.scroll_into_view_if_needed()
			await cb.check(timeout=2000)
			return
		except Exception:
			pass

		# 2) Label click path
		try:
			label = scope.locator(f"label:has-text('{name_pattern}')").first
			await label.scroll_into_view_if_needed()
			await label.click()
			return
		except Exception:
			pass

		# 3) JS set input.checked and dispatch events
		try:
			candidate_row = scope.locator(
				f"xpath=//*[self::label or self::*][contains(normalize-space(.), {repr(name_pattern)})]"
			).first
			inp = candidate_row.locator("css=input[type='checkbox']").first
			await inp.wait_for(state="attached", timeout=3000)
			await inp.evaluate(
				"el => { el.checked = true; el.dispatchEvent(new Event('input', {bubbles:true})); el.dispatchEvent(new Event('change', {bubbles:true})); }"
			)
		except Exception:
			pass

	async def click_apply_in_scope(scope) -> None:
		"""Click Apply/Show Results-like buttons inside a scope, with fallbacks.

		Also tries the nearest button next to the selected checkbox row.
		"""
		print(f"[DEBUG] Attempting to find Apply button in scope...")
		
		patterns = [
			re.compile(r"^\s*Apply\s*$", re.I),
			re.compile(r"^\s*Apply Filter\s*$", re.I),
			re.compile(r"^\s*Show Results\s*$", re.I),
			re.compile(r"^\s*Apply\s*\(\d+\)\s*$", re.I),
		]
		
		# Try role-based selectors first
		for p in patterns:
			try:
				btn = scope.get_by_role("button", name=p).first
				if await btn.count():
					print(f"[DEBUG] Found Apply button with role selector: {p.pattern}")
					await btn.scroll_into_view_if_needed()
					try:
						await btn.wait_for(state="visible", timeout=2000)
					except Exception:
						pass
					
					# Check if button is enabled
					is_disabled = await btn.evaluate("el => !!(el.disabled || el.getAttribute('disabled') !== null)")
					if is_disabled:
						print(f"[DEBUG] Apply button is disabled, waiting...")
						await asyncio.sleep(1)
					
					await btn.click(timeout=3000)
					print(f"[DEBUG] Successfully clicked Apply button")
					return
			except Exception as e:
				print(f"[DEBUG] Role selector failed: {e}")
				continue
		
		# Try CSS selectors
		css_selectors = [
			"css=button:has-text('Apply')",
			"css=button:has-text('Apply Filter')",
			"css=button:has-text('Show Results')",
			"css=button[class*='apply']",
			"css=.apply-btn",
			"css=.filter-apply-btn",
			"css=button[type='submit']",
		]
		
		for selector in css_selectors:
			try:
				btn = scope.locator(selector).first
				if await btn.count():
					print(f"[DEBUG] Found Apply button with CSS selector: {selector}")
					await btn.scroll_into_view_if_needed()
					await btn.wait_for(state="visible", timeout=2000)
					
					# Check if button is enabled
					is_disabled = await btn.evaluate("el => !!(el.disabled || el.getAttribute('disabled') !== null)")
					if is_disabled:
						print(f"[DEBUG] Apply button is disabled, waiting...")
						await asyncio.sleep(1)
					
					await btn.click(timeout=3000)
					print(f"[DEBUG] Successfully clicked Apply button")
					return
			except Exception as e:
				print(f"[DEBUG] CSS selector failed: {e}")
				continue
		
		# Try a button near the checkbox list area
		try:
			row = scope.locator("css=label:has-text('Product Management')").first
			if await row.count():
				container = row.locator("xpath=ancestor::*[self::div or self::section or self::form][1]").first
				btn = container.locator("css=button:has-text('Apply'), css=button:has-text('Show Results')").first
				if await btn.count():
					print(f"[DEBUG] Found Apply button near Product Management checkbox")
					await btn.click(timeout=3000)
					return
		except Exception as e:
			print(f"[DEBUG] Checkbox area search failed: {e}")
			pass
		
		# Fallback: any visible button containing Apply
		try:
			btn2 = scope.locator("css=button:has-text('Apply')").first
			if await btn2.count():
				print(f"[DEBUG] Found Apply button with fallback selector")
				await btn2.click(timeout=3000)
				return
		except Exception as e:
			print(f"[DEBUG] Fallback selector failed: {e}")
			pass
		
		print(f"[DEBUG] No Apply button found in scope")
		# Take a debug screenshot to help troubleshoot
		await debug_screenshot(scope, "no_apply_button_found")

	async def click_modal_apply_and_wait(page: Page, filter_chip_text: str) -> None:
		"""Click the Apply button inside the open filter dialog and wait for results.

		- Locates dialog via role
		- Waits for Apply to become enabled
		- Tries normal click, force click, and JS click
		- Waits for dialog to close and network idle, then verifies chip
		"""
		print(f"[DEBUG] Attempting to click Apply button in modal for filter: {filter_chip_text}")
		
		# Try to find modal dialog
		modal = None
		try:
			modal = page.get_by_role("dialog").first
			await modal.wait_for(state="visible", timeout=6000)
			print(f"[DEBUG] Found modal dialog")
		except Exception:
			print(f"[DEBUG] No modal dialog found, trying alternative selectors")
			# Try alternative modal selectors
			modal_selectors = [
				"css=.modal",
				"css=.dialog",
				"css=.filter-modal",
				"css=.layer",
				"css=[role='dialog']",
				"css=.popup",
			]
			for selector in modal_selectors:
				try:
					modal = page.locator(selector).first
					if await modal.count():
						await modal.wait_for(state="visible", timeout=3000)
						print(f"[DEBUG] Found modal with selector: {selector}")
						break
				except Exception:
					continue
		
		if not modal:
			print(f"[DEBUG] No modal found, falling back to page-level Apply button")
			await click_apply_in_scope(page)
			return
		
		# Find Apply button in modal
		apply_btn = None
		apply_selectors = [
			modal.get_by_role("button", name=re.compile(r"^\s*Apply\s*$", re.I)).first,
			modal.locator("css=button:has-text('Apply')").first,
			modal.locator("css=button:has-text('Apply Filter')").first,
			modal.locator("css=button:has-text('Show Results')").first,
			modal.locator("css=button[type='submit']").first,
		]
		
		for selector in apply_selectors:
			try:
				if await selector.count():
					apply_btn = selector
					print(f"[DEBUG] Found Apply button in modal")
					break
			except Exception:
				continue
		
		if not apply_btn:
			print(f"[DEBUG] No Apply button found in modal")
			return
		
		await apply_btn.wait_for(state="visible", timeout=5000)
		
		# Wait until enabled (button may be disabled until a selection is made)
		print(f"[DEBUG] Checking if Apply button is enabled...")
		for i in range(15):  # Increased retry count
			try:
				is_disabled = await apply_btn.evaluate("el => !!(el.disabled || el.getAttribute('disabled') !== null)")
				if not is_disabled:
					print(f"[DEBUG] Apply button is enabled")
					break
				print(f"[DEBUG] Apply button still disabled, attempt {i+1}/15")
			except Exception:
				pass
			await asyncio.sleep(0.5)  # Increased wait time
		
		# Try click strategies
		clicked = False
		click_strategies = [
			("normal click", lambda: apply_btn.click(timeout=3000)),
			("scroll and click", lambda: apply_btn.scroll_into_view_if_needed()),
			("force click", lambda: apply_btn.click(force=True, timeout=3000)),
			("JS click", lambda: apply_btn.evaluate("el => el.click()")),
			("double click", lambda: apply_btn.dblclick(timeout=3000)),
		]
		
		for strategy_name, strategy_func in click_strategies:
			try:
				print(f"[DEBUG] Trying {strategy_name}...")
				await strategy_func()
				clicked = True
				print(f"[DEBUG] Successfully executed {strategy_name}")
				break
			except Exception as e:
				print(f"[DEBUG] {strategy_name} failed: {e}")
				continue
		
		if not clicked:
			print(f"[DEBUG] All click strategies failed")
			await debug_screenshot(page, "apply_button_click_failed")
			return
		
		# Wait for dialog closed and results loaded
		print(f"[DEBUG] Waiting for modal to close...")
		try:
			await modal.wait_for(state="hidden", timeout=10000)
			print(f"[DEBUG] Modal closed successfully")
		except Exception:
			print(f"[DEBUG] Modal did not close within timeout")
		
		await wait_network_idle(page)
		
		# Verify filter was applied
		try:
			await assert_chip_applied(filter_chip_text)
			print(f"[DEBUG] Filter chip '{filter_chip_text}' confirmed applied")
		except Exception as e:
			print(f"[DEBUG] Could not verify filter chip: {e}")

	async def search_select_apply_in_container(container_locator, search_term: str) -> None:
		# Prefer section-specific placeholders to avoid using the global search
		search_input = container_locator.get_by_placeholder("Search Department", exact=False).first
		if not await search_input.count():
			search_input = container_locator.get_by_placeholder("Search Location", exact=False).first
		if not await search_input.count():
			search_input = container_locator.locator("css=input[placeholder*='Search' i], css=input[type='search']").first
		await search_input.wait_for(state="visible", timeout=5000)
		await search_input.click()
		try:
			await search_input.fill("")
			await search_input.type(search_term, delay=0)
		except Exception:
			# Force focus and set value via JS as a fallback
			el = search_input
			await el.evaluate("e => { e.focus(); e.value=''; }")
			await el.type(search_term, delay=0)
		# Select matching option inside the same container
		option = container_locator.get_by_role(
			"checkbox", name=re.compile(re.escape(search_term), re.I)
		).first
		await option.wait_for(state="attached", timeout=7000)
		await option.check(timeout=3000)
		# Apply button inside the container (or immediate apply if auto-applies)
		try:
			apply_btn = container_locator.get_by_role(
				"button", name=re.compile(r"^\s*Apply\s*$", re.I)
			).first
			await apply_btn.click(timeout=2000)
		except Exception:
			pass

	async def search_select_apply_in_dialog(search_term: str) -> None:
		# Fallback: some UIs open a dialog; scope interactions to that
		panel = page.get_by_role("dialog")
		try:
			await panel.first.wait_for(state="visible", timeout=5000)
		except Exception:
			panel = page.locator("css=.filterContainer, css=.filter-modal, css=.layer")
			await panel.first.wait_for(state="visible", timeout=5000)
		inp = panel.locator("css=input[placeholder*='Search' i], css=input[type='search']").first
		await inp.click()
		await inp.fill("")
		await inp.type(search_term, delay=0)
		opt = panel.get_by_role("checkbox", name=re.compile(re.escape(search_term), re.I)).first
		await opt.wait_for(state="attached", timeout=7000)
		await opt.check(timeout=3000)
		try:
			apply_btn = panel.get_by_role("button", name=re.compile(r"^\s*Apply\s*$", re.I)).first
			await apply_btn.click(timeout=2000)
		except Exception:
			pass

	async def assert_chip_applied(text: str, timeout: int = 8000) -> None:
		end = asyncio.get_event_loop().time() + (timeout / 1000)
		while asyncio.get_event_loop().time() < end:
			for sel in [
				"css=.chip, .filter-chip, .tags, .appliedFilter, .selectedFilters",
				"text=/" + re.escape(text) + "/i",
			]:
				try:
					await page.locator(sel).first.wait_for(state="visible", timeout=1000)
					return
				except Exception:
					continue
			raise RuntimeError(f"Filter not confirmed applied: {text}")

	# Department → View More → search "Product Management" → Apply (robust to UI variants)
	try:
		# Some pages label the section differently; try a few variants
		for section_label in [
			"Department",
			"Departments",
			"Function",
			"Department & Role",
			"Department/Function",
		]:
			try:
				container = await open_view_more_in_section(section_label)
				break
			except Exception:
				container = None
				continue
		if not container:
			# As a last resort, click a generic Department/Function trigger if present
			try:
				trigger = await first_locator(page, department_filter_selectors, timeout=3000)
				await trigger.click()
			except Exception:
				pass

		# Prefer operating in an opened dialog/panel if present; otherwise use the container
		panel = page.get_by_role("dialog").first
		use_panel = True
		try:
			await panel.wait_for(state="visible", timeout=3000)
		except Exception:
			use_panel = False

		if use_panel:
			target_scope = panel
		else:
			# Fall back to the last resolved container or the first matching section
			if not container:
				for section_label in [
					"Department",
					"Departments",
					"Function",
					"Department & Role",
					"Department/Function",
				]:
					try:
						container = page.locator(section_container_xpath(section_label)).first
						await container.wait_for(state="visible", timeout=2000)
						break
					except Exception:
						container = None
						continue
			target_scope = container if container else page

		# Search within the chosen scope
		dept_search = target_scope.get_by_placeholder("Search Department", exact=False).first
		if not await dept_search.count():
			dept_search = target_scope.locator("css=input[placeholder*='Search' i], css=input[type='search']").first
		await dept_search.wait_for(state="visible", timeout=5000)
		await dept_search.click()

		# Robust input: try fill, then JS value+input event, then keyboard typing
		typed = False
		try:
			await dept_search.fill("")
			await dept_search.type("Product Management", delay=0)
			typed = True
		except Exception:
			pass
		if not typed:
			try:
				await dept_search.evaluate(
					"el => { el.focus(); el.value = ''; el.dispatchEvent(new Event('input', {bubbles:true})); }"
				)
				await dept_search.evaluate(
					"el => { el.value = 'Product Management'; el.dispatchEvent(new Event('input', {bubbles:true})); }"
				)
				typed = True
			except Exception:
				pass
		if not typed:
			await target_scope.click()
			await page.keyboard.type("Product Management")

		# No fixed delays; proceed to selection immediately

		# Select the checkbox robustly
		print(f"[DEBUG] Selecting Product Management checkbox...")
		await robust_check_checkbox(target_scope, "Product Management")
		print(f"[DEBUG] Product Management checkbox selected")

		# Wait a moment for the UI to update
		await asyncio.sleep(1)

		# Prefer the dialog-scoped Apply, as per the UI screenshot
		print(f"[DEBUG] Attempting to click Apply button after Product Management selection...")
		try:
			await click_modal_apply_and_wait(page, "Product Management")
			print(f"[DEBUG] Modal Apply button clicked successfully")
		except Exception as e:
			print(f"[DEBUG] Modal Apply failed: {e}")
			# Fallback: try scope/page Apply and then the modal again
			print(f"[DEBUG] Trying fallback Apply strategies...")
			try:
				await click_apply_in_scope(target_scope)
				print(f"[DEBUG] Scope Apply clicked")
			except Exception as e2:
				print(f"[DEBUG] Scope Apply failed: {e2}")
			
			try:
				await click_apply_in_scope(page)
				print(f"[DEBUG] Page Apply clicked")
			except Exception as e3:
				print(f"[DEBUG] Page Apply failed: {e3}")
			
			# Try modal again as final attempt
			try:
				await click_modal_apply_and_wait(page, "Product Management")
				print(f"[DEBUG] Final modal Apply attempt succeeded")
			except Exception as e4:
				print(f"[DEBUG] Final modal Apply attempt failed: {e4}")
				print(f"[DEBUG] All Apply strategies exhausted for Product Management filter")
	except Exception:
		pass

	# Location → View More → select Bengaluru → Apply (no search field per screenshot)
	try:
		await open_view_more_in_section("Location")
		panel = page.get_by_role("dialog").first
		await panel.wait_for(state="visible", timeout=6000)
		blr_option = panel.get_by_role("checkbox", name=re.compile(r"Bengaluru|Bangalore", re.I)).first
		await blr_option.wait_for(state="attached", timeout=6000)
		await blr_option.check(timeout=3000)
		await panel.get_by_role("button", name=re.compile(r"^\s*Apply\s*$", re.I)).first.click(timeout=4000)
		# Verify either Bengaluru or Bangalore chip
		try:
			await assert_chip_applied("Bengaluru")
		except Exception:
			await assert_chip_applied("Bangalore")
	except Exception:
		pass

	# Freshness dropdown → select Last 1 day
	try:
		fresh_section = page.locator(section_container_xpath("Freshness")).first
		await fresh_section.scroll_into_view_if_needed()
		fresh_trigger = fresh_section.get_by_role("button").first
		await fresh_trigger.click(timeout=3000)
		await page.get_by_text(re.compile(r"^\s*Last 1 day\s*$", re.I)).first.click(timeout=4000)
		await assert_chip_applied("Last 1 day")
	except Exception:
		try:
			r = page.get_by_role("radio", name=re.compile(r"Last 1 day", re.I)).first
			await r.check(timeout=3000)
		except Exception:
			pass


async def _find_first_job_link(page: Page) -> Tuple[str, str]:
	# Try curated selectors first
	try:
		job_link = await first_locator(page, job_link_selectors, timeout=6000)
		href = await job_link.get_attribute("href") or ""
		txt = (await job_link.text_content() or "").strip()
		if href:
			return href, txt
	except Exception:
		pass

	# Fallback: scan all anchors and pick first plausible job link
	anchors = await page.locator("a").element_handles()
	for a in anchors:
		try:
			href = await a.get_attribute("href")
			if not href:
				continue
			# Normalize relative links
			if href.startswith("/"):
				href = urljoin(page.url, href)
			href_low = href.lower()
			if ("naukri.com" in href_low) and ("job" in href_low or "jobs" in href_low):
				text = await (await a.text_content()) or ""
				return href, text.strip()
		except Exception:
			continue
	raise RuntimeError("Could not find any plausible job link on the page")


async def collect_first_job_and_apply(page: Page) -> Dict[str, str]:
	# Try card-based selection first
	card = None
	try:
		card = await first_locator(page, first_job_card_selectors, timeout=6000)
	except Exception:
		pass

	title = ""; company = ""; location = ""; link = ""

	if card:
		try:
			candidate_title = await card.locator("css=h3, css=h2").first.text_content()
			title = (candidate_title or "").strip()
		except Exception:
			pass
		try:
			link = await card.locator("css=a[href]").first.get_attribute("href") or ""
		except Exception:
			pass

	if not link:
		# Fallback: find first job link on the page by scanning anchors
		link, title_text = await _find_first_job_link(page)
		if not title:
			title = title_text

	job = {
		"title": title,
		"company": company,
		"location": location,
		"link": link,
	}

	# Open job in new tab and click Apply
	new_page = page
	try:
		if card and link == "":
			async with page.context.expect_page() as new_page_info:
				await card.click()
			new_page = await new_page_info.value
		else:
			# Try opening in same tab first
			await page.goto(link)
			new_page = page
	except Exception:
		# Fallback: if a new page opened unexpectedly, try to grab it
		try:
			async with page.context.expect_page() as new_page_info:
				await page.locator(f"a[href='{link}']").first.click()
			new_page = await new_page_info.value
		except Exception:
			new_page = page
	await wait_network_idle(new_page)

	# Some pages have direct Apply; others have a modal
	try:
		apply_btn = await first_locator(new_page, apply_button_selectors, timeout=6000)
		await apply_btn.click()
		await wait_network_idle(new_page)
	except Exception:
		pass

	return job

