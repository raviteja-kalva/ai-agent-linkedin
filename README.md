# Naukri Automation Agent (Python + Playwright)

Automates login to Naukri, applies search filters, applies to the first listed job, generates an Excel report, and emails it.

## Features
- Secure credential handling via `.env` and runtime prompts (never hardcoded)
- Playwright automation with resilient selectors, retries, and network idleness waits
- Filters: Role "Product Manager", Location "Bangalore/Bengaluru", Department "Product Management", Freshness "Last 1 day"
- Handles new tabs/popups during Apply flow
- Generates Excel report for the applied job
- Emails the report via SMTP

## Prerequisites
- Windows 10/11
- Python 3.9+
- Playwright browsers (installed via `playwright install`)

If `python` is not available in your PATH, install Python from Microsoft Store or python.org. You can also try `py -3` on Windows.

## Setup
```bash
# Ensure Python is available: `python --version` or `py -3 --version`

# Create virtual environment (choose one)
python -m venv .venv
# or
py -3 -m venv .venv

# Activate
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install
```

## Environment Variables
Copy `.env.example` to `.env` and fill in values:

```
# Naukri
NAUKRI_EMAIL=
NAUKRI_PASSWORD=
NAUKRI_JOB_URL=

# Mail (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_TO=raviteja.kalva@gmail.com
```

- If any are missing at runtime, the CLI will prompt you securely.
- For Gmail, create an App Password if 2FA is enabled.

## Usage
```bash
# Activate venv first
.venv\Scripts\activate

# Run the agent with optional flags
python -m src.cli --headful --timeout 45000
```

Optional flags:
- `--url` Naukri search URL (validated). If omitted, a default is used and validated.
- `--headful` Launch browser with UI (default: headless)
- `--timeout` Per-action timeout in ms (default: 30000)

## Output
- Excel report written to `reports/applied_job_<timestamp>.xlsx`
- The same report is emailed to the configured recipient

## Notes on Reliability
- Uses role-, label-, and text-based selectors first, with CSS/XPath as fallback
- Waits for network idleness and DOM stability before proceeding
- Retries critical actions with exponential backoff
- Logs structured events to console

## Troubleshooting
- If login fails, ensure credentials are correct and your account doesn’t require additional verification
- If locators change, the agent uses multiple fallbacks; update `selectors.py` if needed
- For CAPTCHA or bot detection, switch to `--headful`, add delays, or perform initial human verification manually

## Legal
Use responsibly and in accordance with Naukri’s Terms of Service.


