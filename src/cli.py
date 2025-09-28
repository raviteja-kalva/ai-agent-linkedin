import argparse
import asyncio
from typing import Optional
from rich import print as rprint
from .config import load_config
from .automation_clean import (
	launch_browser,
	open_linkedin_and_login,
	navigate_to_jobs,
	apply_filters,
	find_and_apply_to_first_job,
)
from .search_simple import search_jobs_simple
from .report import write_excel_report


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="LinkedIn job automation agent")
	parser.add_argument("--headful", action="store_true", help="Run browser in headed mode")
	parser.add_argument("--timeout", type=int, default=30000, help="Per action timeout in ms")
	return parser.parse_args()


async def main_async(headful: bool, timeout_ms: int) -> int:
	cfg = load_config()
	cfg.headless = not headful
	cfg.action_timeout_ms = timeout_ms

	async with launch_browser(headless=cfg.headless) as (browser, context):
		# Step 1: Login to LinkedIn
		page = await open_linkedin_and_login(context, cfg.linkedin_email, cfg.linkedin_password)
		
		# Step 2: Navigate to Jobs
		await navigate_to_jobs(page)
		
		# Step 3: Search for jobs (skip this step as we'll navigate directly to the jobs page)
		# await search_jobs_simple(page, "Product Manager", "India")
		
		# Step 4: Apply filters
		await apply_filters(page)
		
		# Step 5: Apply to first job
		job = await find_and_apply_to_first_job(page)
		rprint(f"[bold]Applied to:[/bold] {job}")

		# Generate report
		report_path = write_excel_report(job)
		rprint(f"[bold green]Report:[/bold green] {report_path}")

	return 0


def main() -> None:
	args = parse_args()
	code = asyncio.run(main_async(args.headful, args.timeout))
	exit(code)


if __name__ == "__main__":
	main()