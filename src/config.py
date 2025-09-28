import os
import getpass
from typing import Optional
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
from credentials import LINKEDIN_EMAIL, LINKEDIN_PASSWORD


class AppConfig(BaseModel):
	linkedin_email: str
	linkedin_password: str
	headless: bool = Field(default=True)
	action_timeout_ms: int = Field(default=30000)


def _prompt_if_missing(current: Optional[str], prompt: str, secret: bool = False) -> str:
	if current:
		return current
	try:
		return getpass.getpass(prompt + ": ") if secret else input(prompt + ": ")
	except Exception:
		return current or ""


def load_config() -> AppConfig:
	load_dotenv()

	# Use stored credentials first, then fallback to environment variables, then prompt
	linkedin_email = LINKEDIN_EMAIL if LINKEDIN_EMAIL != "your_email@example.com" else (
		os.getenv("LINKEDIN_EMAIL") or _prompt_if_missing(None, "Enter LinkedIn email")
	)
	linkedin_password = LINKEDIN_PASSWORD if LINKEDIN_PASSWORD != "your_password" else (
		os.getenv("LINKEDIN_PASSWORD") or _prompt_if_missing(None, "Enter LinkedIn password", secret=True)
	)

	try:
		cfg = AppConfig(
			linkedin_email=linkedin_email,
			linkedin_password=linkedin_password,
		)
	except ValidationError as e:
		raise RuntimeError(f"Invalid configuration: {e}")

	return cfg