#!/usr/bin/env python3
"""
Create sample schedule.xlsx file for testing.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import openpyxl


def create_sample_schedule(data_dir: Path = Path("./data")):
    """Create sample schedule.xlsx with example entries."""

    schedule_file = data_dir / "schedule.xlsx"

    if schedule_file.exists():
        response = input(f"{schedule_file} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Schedule"

    # Headers
    ws.append(["Date", "Path", "Track Name", "Enabled"])

    # Sample entries
    today = datetime.now()

    entries = [
        # Today's entries
        (today, "audio/", "morning_brief.mp3", True),
        (today, "audio/", "news_update.mp3", True),
        (today, "audio/podcasts/", "daily_podcast.mp3", True),

        # Tomorrow's entries
        (today + timedelta(days=1), "audio/", "morning_brief.mp3", True),
        (today + timedelta(days=1), "audio/news/", "evening_news.mp3", True),

        # Future entries
        (today + timedelta(days=2), "audio/", "weekly_summary.mp3", True),
        (today + timedelta(days=3), "audio/", "morning_brief.mp3", False),  # Disabled
    ]

    for date, path, track_name, enabled in entries:
        ws.append([date.strftime("%Y-%m-%d"), path, track_name, enabled])

    # Format headers
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass

        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Create data directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)

    # Save workbook
    wb.save(schedule_file)

    print(f"✓ Created {schedule_file}")
    print(f"\nSample schedule created with {len(entries)} entries:")
    print(f"  - {len([e for e in entries if e[0] == today])} entries for today")
    print(f"  - {len([e for e in entries if e[3]])} enabled entries")
    print(f"  - {len([e for e in entries if not e[3]])} disabled entries")
    print("\nNote: Update the track names to match your actual audio files!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        data_dir = Path("./data")

    print(f"Creating sample schedule in: {data_dir}")
    create_sample_schedule(data_dir)
