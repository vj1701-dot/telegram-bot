"""Parse schedule.xlsx file."""
import logging
from pathlib import Path
from datetime import datetime
from openpyxl import load_workbook
from typing import List

from shared.models import ScheduleEntry

logger = logging.getLogger(__name__)


class ExcelParser:
    """Parses Excel schedule file."""

    def __init__(self, excel_path: Path = Path("/app/data/schedule.xlsx")):
        self.excel_path = excel_path

    def get_all_entries(self) -> List[ScheduleEntry]:
        """Get all schedule entries from Excel."""
        if not self.excel_path.exists():
            logger.warning(f"Schedule file not found: {self.excel_path}")
            return []

        try:
            wb = load_workbook(self.excel_path, read_only=True)
            ws = wb.active

            entries = []
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                entry = self._parse_row(row, row_idx)
                if entry:
                    entries.append(entry)

            wb.close()
            logger.info(f"Parsed {len(entries)} entries from schedule")
            return entries

        except Exception as e:
            logger.error(f"Failed to parse Excel: {e}")
            return []

    def get_today_entries(self) -> List[ScheduleEntry]:
        """Get entries scheduled for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        all_entries = self.get_all_entries()

        today_entries = [e for e in all_entries
                        if e.date == today and e.enabled]

        logger.info(f"Found {len(today_entries)} entries for today ({today})")
        return today_entries

    def get_entries_by_date(self, date_str: str) -> List[ScheduleEntry]:
        """Get entries for a specific date (YYYY-MM-DD format)."""
        all_entries = self.get_all_entries()
        return [e for e in all_entries if e.date == date_str and e.enabled]

    def _parse_row(self, row, row_idx: int) -> ScheduleEntry:
        """Parse a single Excel row into ScheduleEntry."""
        # Expected columns: Date, Path, Track Name, Enabled
        try:
            if not row or len(row) < 3:
                return None

            date_cell = row[0]
            path_cell = row[1]
            track_cell = row[2]
            enabled_cell = row[3] if len(row) > 3 else True

            if not all([date_cell, path_cell, track_cell]):
                return None

            # Handle datetime objects from Excel
            if isinstance(date_cell, datetime):
                date_str = date_cell.strftime("%Y-%m-%d")
            else:
                date_str = str(date_cell)

            return ScheduleEntry(
                date=date_str,
                path=str(path_cell),
                track_name=str(track_cell),
                enabled=bool(enabled_cell)
            )
        except Exception as e:
            logger.error(f"Failed to parse row {row_idx}: {e}")
            return None
