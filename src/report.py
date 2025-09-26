from datetime import datetime
from pathlib import Path
from typing import Dict
from openpyxl import Workbook


def write_excel_report(job: Dict[str, str], out_dir: Path = Path("reports")) -> Path:
	out_dir.mkdir(parents=True, exist_ok=True)
	stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	out_path = out_dir / f"applied_job_{stamp}.xlsx"

	wb = Workbook()
	ws = wb.active
	ws.title = "Applied Job"

	ws.append(["Field", "Value"]) 
	for key in ["title", "company", "location", "link"]:
		ws.append([key, job.get(key, "")])

	wb.save(out_path)
	return out_path


