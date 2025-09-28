from datetime import datetime
from pathlib import Path
from typing import Dict
from openpyxl import Workbook


def write_excel_report(job: Dict[str, str], out_dir: Path = Path("reports")) -> Path:
	"""Generate Excel report for applied job"""
	out_dir.mkdir(parents=True, exist_ok=True)
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	out_path = out_dir / f"linkedin_job_{timestamp}.xlsx"

	wb = Workbook()
	ws = wb.active
	ws.title = "Applied Job"

	# Headers
	ws.append(["Field", "Value"])
	
	# Job details
	ws.append(["Job Title", job.get("title", "")])
	ws.append(["Company", job.get("company", "")])
	ws.append(["Location", job.get("location", "")])
	ws.append(["Applied Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
	ws.append(["Platform", "LinkedIn"])

	wb.save(out_path)
	return out_path
