"""Tests for Excel parser."""
import pytest
from pathlib import Path
from datetime import datetime
import openpyxl
from bot.utils.excel_parser import ExcelParser
from shared.models import ScheduleEntry


class TestExcelParser:
    """Test Excel parsing functionality."""

    def test_parser_initialization(self):
        """Test parser initializes with correct path."""
        parser = ExcelParser()
        assert parser.excel_path == Path("/app/data/schedule.xlsx")

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file returns empty list."""
        parser = ExcelParser(Path("/nonexistent/file.xlsx"))
        entries = parser.get_all_entries()
        assert entries == []

    def test_get_today_entries_filters_by_date(self, tmp_path):
        """Test that get_today_entries filters by current date."""
        # Create sample schedule
        schedule_file = tmp_path / "schedule.xlsx"
        _create_test_schedule(schedule_file)

        parser = ExcelParser(schedule_file)
        today_entries = parser.get_today_entries()

        # All entries should be for today
        today_str = datetime.now().strftime("%Y-%m-%d")
        for entry in today_entries:
            assert entry.date == today_str

    def test_schedule_entry_builds_correct_path(self):
        """Test that ScheduleEntry builds correct full path."""
        entry = ScheduleEntry(
            date="2024-01-15",
            path="audio/",
            track_name="test.mp3",
            enabled=True
        )

        full_path = entry.build_full_path()
        assert full_path == "/app/data/audio/test.mp3"


def _create_test_schedule(file_path: Path):
    """Helper to create test schedule file."""
    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(["Date", "Path", "Track Name", "Enabled"])

    today = datetime.now().strftime("%Y-%m-%d")
    ws.append([today, "audio/", "test1.mp3", True])
    ws.append([today, "audio/", "test2.mp3", False])
    ws.append(["2024-12-31", "audio/", "future.mp3", True])

    wb.save(file_path)
