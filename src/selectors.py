from typing import List

# Prefer role-, label-, and text-based locators; keep CSS/XPath fallbacks.

login_button_selectors: List[str] = [
	"role=button[name=/login|sign in/i]",
	"text=/login|sign in/i",
	"css=button[aria-label*='Login']",
	"css=a[title*='Login']",
]

email_input_selectors: List[str] = [
	"role=textbox[name=/email|username/i]",
	"css=input[type='email']",
	"css=input[name*='email']",
	"css=input[name*='username']",
]

password_input_selectors: List[str] = [
	"role=textbox[name=/password/i]",
	"css=input[type='password']",
	"css=input[name*='password']",
]

submit_login_selectors: List[str] = [
	"role=button[name=/login|submit|continue/i]",
	"css=button[type='submit']",
]

search_role_input: List[str] = [
	"role=textbox[name=/search|job/i]",
	"css=input#qsb-keyskill-sugg",
	"css=input[placeholder*='Enter keyword']",
	"css=input[placeholder*='designation']",
	"css=input[placeholder*='Search jobs']",
	"css=input[placeholder*='Search']",
	"css=input[aria-label*='Search']",
	"css=input[name='qp']",
	"css=input[name='keyword']",
	"css=input[name*='search']",
]

search_submit_selectors: List[str] = [
	"role=button[name=/search/i]",
	"css=button#qsbFormBtn",
	"css=button[type='submit']",
	"text=/^\s*Search\s*$/i",
]

location_filter_selectors: List[str] = [
	"role=button[name=/location/i]",
	"text=/location/i",
]

department_filter_selectors: List[str] = [
	"role=button[name=/department|function/i]",
	"text=/department|function/i",
]

freshness_filter_selectors: List[str] = [
	"role=button[name=/freshness/i]",
	"text=/freshness/i",
]

apply_button_selectors: List[str] = [
	"role=button[name=/apply/i]",
	"text=/apply now|apply/i",
	"css=button[title*='Apply']",
	"css=button:has-text('Apply')",
	"css=button:has-text('Apply Filter')",
	"css=button:has-text('Show Results')",
	"css=button[data-testid*='apply']",
	"css=button[class*='apply']",
	"css=.apply-btn",
	"css=.filter-apply-btn",
	"css=button[type='submit']",
]

first_job_card_selectors: List[str] = [
	"css=article:has([data-job-id])",
	"css=[data-job-id]",
	"css=.jobTuple",
]

# New: job link patterns commonly present in Naukri listings
job_link_selectors: List[str] = [
	"css=a.title",
	"css=a[title][href*='job-listings']",
	"css=a[href*='naukri.com'][href*='job-']",
	"css=a[href*='/jobs/']",
]

