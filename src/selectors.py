from typing import List

# LinkedIn-specific selectors for job automation

# Login selectors
login_button_selectors: List[str] = [
	"css=a[href*='login']",
	"text=Sign in",
	"css=button:has-text('Sign in')",
	"css=a:has-text('Sign in')",
	"css=.sign-in-link",
	"css=[data-test-id='sign-in-link']",
]

email_input_selectors: List[str] = [
	"css=input[name='session_key']",
	"css=input[type='email']",
	"css=input[autocomplete='username']",
	"css=input[id='username']",
	"css=input[placeholder*='Email']",
	"css=input[placeholder*='email']",
]

password_input_selectors: List[str] = [
	"css=input[name='session_password']",
	"css=input[type='password']",
	"css=input[autocomplete='current-password']",
	"css=input[id='password']",
	"css=input[placeholder*='Password']",
	"css=input[placeholder*='password']",
]

submit_login_selectors: List[str] = [
	"css=button[type='submit']",
	"css=button:has-text('Sign in')",
	"css=input[type='submit']",
	"css=button:has-text('Sign In')",
	"css=.sign-in-form__submit-button",
	"css=button[data-test-id='sign-in-submit']",
]

# Jobs navigation
jobs_menu_selectors: List[str] = [
	"css=a[href*='/jobs/']",
	"text=Jobs",
	"css=nav a:has-text('Jobs')",
]

# Job search selectors
job_title_input_selectors: List[str] = [
	"css=input[placeholder*='Title, skill or Company']",
	"css=input[placeholder*='Title, skill or company']",
	"css=input[placeholder*='Search jobs']",
	"css=input[placeholder*='job title']",
	"css=input[name='keywords']",
	"css=input[placeholder*='Job title']",
	"css=input[placeholder*='Job title, skills, or company']",
	"css=input[placeholder*='Search job titles']",
	"css=input[data-test-id='jobs-search-box-keyword-id']",
	"css=input[aria-label*='job title']",
	"css=input[aria-label*='Search jobs']",
]

location_input_selectors: List[str] = [
	"css=input[placeholder*='City, state, or zip code']",
	"css=input[placeholder*='Location']",
	"css=input[placeholder*='city']",
	"css=input[name='location']",
	"css=input[placeholder*='Where']",
	"css=input[data-test-id='jobs-search-box-location-id']",
	"css=input[aria-label*='Location']",
	"css=input[aria-label*='Where']",
]

search_button_selectors: List[str] = [
	"css=button:has-text('Search')",
	"css=button[type='submit']",
	"css=.jobs-search-box__submit-button",
	"css=button[data-test-id='jobs-search-box-submit-button']",
	"css=button[aria-label*='Search']",
	"css=button:has-text('Search jobs')",
]

# Filter selectors
date_posted_filter_selectors: List[str] = [
	"css=button:has-text('Date posted')",
	"css=button:has-text('Date')",
	"css=.jobs-search-date-posted-filter",
	"css=button[aria-label*='Date posted']",
	"css=button[data-test-id*='date-posted']",
	"css=button:has-text('Posted')",
]

date_posted_options: List[str] = [
	"text=Past 24 hours",
	"text=Past week", 
	"text=Past month",
	"css=button:has-text('Past 24 hours')",
	"css=li:has-text('Past 24 hours')",
	"css=option:has-text('Past 24 hours')",
]

easy_apply_filter_selectors: List[str] = [
	"css=button:has-text('Easy Apply')",
	"css=input[type='checkbox']:near(text='Easy Apply')",
	"css=label:has-text('Easy Apply')",
	"css=input[type='checkbox'][aria-label*='Easy Apply']",
	"css=button[aria-label*='Easy Apply']",
	"css=.jobs-search-advanced-filters__easy-apply-filter",
]

all_filters_selectors: List[str] = [
	"css=button:has-text('All filters')",
	"css=button:has-text('All Filters')",
	"css=.jobs-search-advanced-filters__button",
	"css=button[aria-label*='All filters']",
	"css=button[data-test-id*='all-filters']",
	"css=button:has-text('More filters')",
]

sort_dropdown_selectors: List[str] = [
	"css=select[name='sortBy']",
	"css=.jobs-search-sort-by",
	"css=select:has-text('Sort by')",
	"css=button:has-text('Sort by')",
	"css=button[aria-label*='Sort by']",
	"css=.jobs-search-sort-dropdown",
]

sort_options: List[str] = [
	"text=Most recent",
	"text=Most Recent",
	"css=option:has-text('Most recent')",
	"css=button:has-text('Most recent')",
	"css=li:has-text('Most recent')",
	"css=option:has-text('Most Recent')",
]

show_results_selectors: List[str] = [
	"css=button:has-text('Show results')",
	"css=button:has-text('Show Results')",
	"css=.jobs-search-advanced-filters__apply-button",
	"css=button[aria-label*='Show results']",
	"css=button[data-test-id*='show-results']",
	"css=button:has-text('Apply filters')",
	"css=button:has-text('Search')",
	"css=button:has-text('Show')",
	"css=button[type='submit']",
	"css=button:has-text('results')",
]

# Job listing selectors
job_card_selectors: List[str] = [
	"css=.jobs-search-results__list-item",
	"css=.job-card-container",
	"css=[data-job-id]",
	"css=.jobs-search-results__list-item--active",
]

job_title_selectors: List[str] = [
	"css=.job-card-list__title",
	"css=.jobs-unified-top-card__job-title",
	"css=h3",
	"css=a[data-control-name='job_card_click']",
]

company_name_selectors: List[str] = [
	"css=.job-card-container__company-name",
	"css=.jobs-unified-top-card__company-name",
	"css=.job-card-list__company-name",
]

location_selectors: List[str] = [
	"css=.job-card-container__metadata-item",
	"css=.jobs-unified-top-card__bullet",
	"css=.job-card-list__metadata-item",
]

# Apply button selectors
apply_button_selectors: List[str] = [
	# SPECIFIC TO JOB DESCRIPTION PANEL ONLY - avoid filter buttons
	"css=.jobs-unified-top-card__apply-button:has-text('Easy Apply')",
	"css=.jobs-unified-top-card__apply-button:has-text('Apply')",
	"css=.jobs-apply-button:has-text('Easy Apply')",
	"css=.jobs-apply-button:has-text('Apply')",
	"css=button[data-control-name='jobdetails_topcard_inapply']:has-text('Easy Apply')",
	"css=button[data-control-name='jobdetails_topcard_inapply']:has-text('Apply')",
	"css=.jobs-unified-top-card__apply-button--full-width:has-text('Easy Apply')",
	"css=.jobs-unified-top-card__apply-button--full-width:has-text('Apply')",
	# Specific to job details panel
	"css=.jobs-details__main-content button:has-text('Easy Apply')",
	"css=.jobs-details__main-content button:has-text('Apply')",
	"css=.jobs-details button:has-text('Easy Apply')",
	"css=.jobs-details button:has-text('Apply')",
	# More specific selectors for job panel
	"css=.jobs-unified-top-card button:has-text('Easy Apply')",
	"css=.jobs-unified-top-card button:has-text('Apply')",
	"css=.jobs-apply-button--top-card:has-text('Easy Apply')",
	"css=.jobs-apply-button--top-card:has-text('Apply')",
	# Data attributes specific to job panel
	"css=button[data-easy-apply-id]:has-text('Easy Apply')",
	"css=button[data-easy-apply-id]:has-text('Apply')",
	"css=button[data-control-name*='jobdetails']:has-text('Easy Apply')",
	"css=button[data-control-name*='jobdetails']:has-text('Apply')",
	# Aria labels specific to job panel
	"css=button[aria-label*='Easy Apply']:has-text('Easy Apply')",
	"css=button[aria-label*='Apply']:has-text('Apply')",
	# Class-based selectors for job panel
	"css=button[class*='jobs-apply-button']:has-text('Easy Apply')",
	"css=button[class*='jobs-apply-button']:has-text('Apply')",
	"css=button[class*='apply-button']:has-text('Easy Apply')",
	"css=button[class*='apply-button']:has-text('Apply')",
	# LinkedIn logo specific to job panel
	"css=button:has-text('Easy Apply'):has(svg)",
	"css=button:has-text('Easy Apply'):has(.linkedin-icon)",
	"css=button:has-text('Easy Apply'):has(.icon)",
	# Fallback - but only in job details area
	"css=.jobs-unified-top-card *:has-text('Easy Apply')",
	"css=.jobs-details *:has-text('Easy Apply')",
	"css=.jobs-details__main-content *:has-text('Easy Apply')",
]

# Modal/overlay selectors
modal_selectors: List[str] = [
	"css=.jobs-easy-apply-modal",
	"css=.jobs-apply-modal",
	"css=[role='dialog']",
	"css=.jobs-easy-apply-modal__content",
	"css=.jobs-apply-modal__content",
	"css=.modal-overlay",
	"css=.jobs-easy-apply-modal__container",
	"css=.jobs-apply-modal__container",
	"css=.jobs-easy-apply-modal__form",
	"css=.jobs-apply-modal__form",
	"css=[data-test-id='easy-apply-modal']",
	"css=[data-test-id='apply-modal']",
]

next_button_selectors: List[str] = [
	"css=button:has-text('Next')",
	"css=button:has-text('Continue')",
	"css=.jobs-easy-apply-modal__footer-button--next",
	"css=button[aria-label*='Next']",
	"css=button[aria-label*='Continue']",
	"css=.jobs-easy-apply-modal__footer-button",
	"css=button:has-text('Next step')",
	"css=button:has-text('Continue to next step')",
	"css=button[data-control-name='continue_unify']",
]

submit_application_selectors: List[str] = [
	"css=button:has-text('Submit application')",
	"css=button:has-text('Submit')",
	"css=.jobs-easy-apply-modal__footer-button--submit",
	"css=button[aria-label*='Submit']",
	"css=button:has-text('Submit your application')",
	"css=button:has-text('Send application')",
	"css=button[data-control-name='submit_unify']",
	"css=button:has-text('Apply')",
	"css=button:has-text('Complete application')",
]

close_modal_selectors: List[str] = [
	"css=button[aria-label='Dismiss']",
	"css=button:has-text('×')",
	"css=.jobs-easy-apply-modal__close-button",
	"css=button[aria-label*='Close']",
	"css=button[aria-label*='Dismiss']",
	"css=button:has-text('Close')",
	"css=button:has-text('Cancel')",
	"css=.modal-close-button",
	"css=button[data-control-name='dismiss_apply_modal']",
]
