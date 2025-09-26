import argparse
import asyncio
from typing import Optional
from rich import print as rprint
from .config import load_config, validate_or_default_url
from .automation import (
	launch_browser,
	open_home_and_login,
	open_url,
	search_jobs,
	apply_left_nav_filters,
	collect_first_job_and_apply,
)
from .report import write_excel_report
from .mailer import send_email_with_attachment


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Naukri automation agent")
	parser.add_argument("--url", type=str, required=False, help="Naukri search URL (optional)")
	parser.add_argument("--headful", action="store_true", help="Run browser in headed mode")
	parser.add_argument("--timeout", type=int, default=30000, help="Per action timeout in ms")
	return parser.parse_args()


async def main_async(url_override: Optional[str], headful: bool, timeout_ms: int) -> int:
	cfg = load_config()
	cfg.headless = not headful
	cfg.action_timeout_ms = timeout_ms

	async with launch_browser(headless=cfg.headless) as (browser, context):
		page = await open_home_and_login(context, cfg.naukri_email, cfg.naukri_password)
		await search_jobs(page, "Product Manager")
		await apply_left_nav_filters(page)
		job = await collect_first_job_and_apply(page)
		rprint(f"[bold]Applied to:[/bold] {job}")

		report_path = write_excel_report(job)
		rprint(f"[bold green]Report:[/bold green] {report_path}")

		# Conditionally send email if SMTP is configured
		smtp = cfg.smtp
		if smtp.mail_from and smtp.mail_to and smtp.username and smtp.password:
			try:
				send_email_with_attachment(
					smtp,
					subject="Naukri Applied Job Report",
					body="Attached is the Excel report for the applied job.",
					attachment=report_path,
				)
				rprint("[bold blue]Email sent successfully[/bold blue]")
			except Exception as e:
				rprint(f"[bold red]Email skipped due to error:[/bold red] {e}")
		else:
			rprint("[yellow]SMTP not configured. Skipping email step.[/yellow]")

	return 0


def main() -> None:
	args = parse_args()
	code = asyncio.run(main_async(args.url, args.headful, args.timeout))
	exit(code)


if __name__ == "__main__":
	main()

