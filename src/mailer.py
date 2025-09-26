import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional
from .config import SMTPConfig


def send_email_with_attachment(
	smtp_cfg: SMTPConfig,
	subject: str,
	body: str,
	attachment: Path,
) -> None:
	if not smtp_cfg.mail_from or not smtp_cfg.mail_to:
		raise RuntimeError("SMTP_FROM and SMTP_TO must be set")

	msg = EmailMessage()
	msg["From"] = smtp_cfg.mail_from
	msg["To"] = smtp_cfg.mail_to
	msg["Subject"] = subject
	msg.set_content(body)

	with attachment.open("rb") as f:
		data = f.read()
		msg.add_attachment(
			data,
			maintype="application",
			subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			filename=attachment.name,
		)

	with smtplib.SMTP(smtp_cfg.host, smtp_cfg.port) as server:
		server.starttls()
		if smtp_cfg.username and smtp_cfg.password:
			server.login(smtp_cfg.username, smtp_cfg.password)
		server.send_message(msg)


