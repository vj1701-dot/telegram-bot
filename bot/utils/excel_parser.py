"""Parse schedule files - supports .xlsx, .ods, and .csv files."""
import logging
from pathlib import Path
from datetime import datetime
from typing import List

from shared.models import ScheduleEntry

logger = logging.getLogger(__name__)


class ExcelParser:
    """Parses schedule files - supports .xlsx, .ods, and .csv formats."""

    def __init__(self, data_dir: Path = Path("/app/data")):
        self.data_dir = data_dir

    def get_all_schedule_files(self) -> List[Path]:
        """Get all schedule files (.xlsx, .ods, .csv) in data directory."""
        schedule_files = []
        for pattern in ["schedule*.xlsx", "schedule*.ods", "schedule*.csv"]:
            schedule_files.extend(list(self.data_dir.glob(pattern)))
        logger.info(f"Found {len(schedule_files)} schedule file(s): {[f.name for f in schedule_files]}")
        return schedule_files

    def get_all_entries(self) -> List[ScheduleEntry]:
        """Get all schedule entries from ALL Excel files."""
        all_entries = []
        schedule_files = self.get_all_schedule_files()

        if not schedule_files:
            logger.warning("No schedule files found")
            return []

        for excel_path in schedule_files:
            entries = self._parse_file(excel_path)
            all_entries.extend(entries)
            logger.info(f"Loaded {len(entries)} entries from {excel_path.name}")

        logger.info(f"Total: {len(all_entries)} entries from {len(schedule_files)} file(s)")
        return all_entries

    def _parse_file(self, excel_path: Path) -> List[ScheduleEntry]:
        """Parse a single schedule file (.xlsx, .ods, or .csv)."""
        if not excel_path.exists():
            logger.warning(f"Schedule file not found: {excel_path}")
            return []

        try:
            import pandas as pd

            # Read based on file extension
            file_ext = excel_path.suffix.lower()
            if file_ext == '.csv':
                df = pd.read_csv(excel_path)
            elif file_ext == '.ods':
                df = pd.read_excel(excel_path, engine='odf')
            else:  # .xlsx
                df = pd.read_excel(excel_path)

            entries = []
            for row_idx, row in df.iterrows():
                entry = self._parse_row_dict(row, row_idx + 2)  # +2 for header + 0-indexing
                if entry:
                    entries.append(entry)

            return entries

        except Exception as e:
            logger.error(f"Failed to parse {excel_path.name}: {e}")
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

    def _parse_row_dict(self, row, row_idx: int) -> ScheduleEntry:
        """Parse a pandas DataFrame row into ScheduleEntry."""
        # Expected columns: Date, Path, Track Name, Enabled
        try:
            import pandas as pd

            # Check if row has required columns
            if pd.isna(row.get('Date')) or pd.isna(row.get('Path')) or pd.isna(row.get('Track Name')):
                return None

            date_cell = row.get('Date')
            path_cell = row.get('Path')
            track_cell = row.get('Track Name')
            enabled_cell = row.get('Enabled', True)

            # Handle datetime objects from Excel
            if isinstance(date_cell, datetime):
                date_str = date_cell.strftime("%Y-%m-%d")
            elif pd.notna(date_cell):
                date_str = str(date_cell)
            else:
                return None

            return ScheduleEntry(
                date=date_str,
                path=str(path_cell),
                track_name=str(track_cell),
                enabled=bool(enabled_cell)
            )
        except Exception as e:
            logger.error(f"Failed to parse row {row_idx}: {e}")
            return None

    def _parse_row(self, row, row_idx: int) -> ScheduleEntry:
        """Parse a single Excel row into ScheduleEntry (legacy method)."""
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
