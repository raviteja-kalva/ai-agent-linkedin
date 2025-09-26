import os
import getpass
from typing import Optional
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv


class SMTPConfig(BaseModel):
	host: str = Field(default="smtp.gmail.com")
	port: int = Field(default=587)
	username: Optional[str] = None
	password: Optional[str] = None
	mail_from: Optional[str] = None
	mail_to: str = Field(default="raviteja.kalva@gmail.com")


class AppConfig(BaseModel):
	naukri_email: str
	naukri_password: str
	naukri_job_url: Optional[str] = None
	smtp: SMTPConfig = Field(default_factory=SMTPConfig)
	headless: bool = Field(default=True)
	action_timeout_ms: int = Field(default=30000)


DEFAULT_SEARCH_URL = (
	"https://www.naukri.com/product-manager-jobs-in-bangalore?k=product%20manager&l=bangalore"
)


def _prompt_if_missing(current: Optional[str], prompt: str, secret: bool = False) -> str:
	if current:
		return current
	try:
		return getpass.getpass(prompt + ": ") if secret else input(prompt + ": ")
	except Exception:
		return current or ""


def load_config() -> AppConfig:
	load_dotenv()

	naukri_email = os.getenv("NAUKRI_EMAIL") or _prompt_if_missing(
		None, "Enter Naukri email"
	)
	naukri_password = os.getenv("NAUKRI_PASSWORD") or _prompt_if_missing(
		None, "Enter Naukri password", secret=True
	)
	env_url = os.getenv("NAUKRI_JOB_URL")
	# Only keep if looks like absolute URL; otherwise let downstream provide default
	naukri_job_url = env_url if (env_url and env_url.startswith("http")) else None

	smtp = SMTPConfig(
		host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
		port=int(os.getenv("SMTP_PORT", "587")),
		username=os.getenv("SMTP_USERNAME"),
		password=os.getenv("SMTP_PASSWORD"),
		mail_from=os.getenv("SMTP_FROM"),
		mail_to=os.getenv("SMTP_TO", "raviteja.kalva@gmail.com"),
	)

	try:
		cfg = AppConfig(
			naukri_email=naukri_email,
			naukri_password=naukri_password,
			naukri_job_url=naukri_job_url,
			smtp=smtp,
		)
	except ValidationError as e:
		raise RuntimeError(f"Invalid configuration: {e}")

	return cfg


def validate_or_default_url(url_override: Optional[str]) -> str:
	candidate = url_override or os.getenv("NAUKRI_JOB_URL") or DEFAULT_SEARCH_URL
	if not candidate.startswith("http"):
		return DEFAULT_SEARCH_URL
	return candidate

