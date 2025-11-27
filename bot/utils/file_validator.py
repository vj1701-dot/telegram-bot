"""File validation and existence checking."""
import logging
from pathlib import Path
from shared.constants import SUPPORTED_FORMATS

logger = logging.getLogger(__name__)


class FileValidator:
    """Validates audio files."""

    DATA_DIR = Path("/app/data")

    def verify_file(self, file_path: str) -> bool:
        """Check if file exists and has valid extension."""
        path = Path(file_path)

        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        if path.suffix.lower() not in SUPPORTED_FORMATS:
            logger.warning(f"Invalid file extension: {file_path}")
            return False

        return True

    def verify_schedule_files(self) -> dict:
        """Check existence of all files referenced in schedule."""
        from bot.utils.excel_parser import ExcelParser

        parser = ExcelParser()
        entries = parser.get_all_entries()

        results = {}
        for entry in entries:
            file_path = entry.build_full_path()
            results[file_path] = self.verify_file(file_path)

        return results

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        path = Path(file_path)
        if path.exists():
            return path.stat().st_size
        return 0

    def list_audio_files(self, directory: str = None) -> list:
        """List all audio files in directory."""
        if directory:
            search_dir = Path(directory)
        else:
            search_dir = self.DATA_DIR

        audio_files = []
        for ext in SUPPORTED_FORMATS:
            audio_files.extend(search_dir.rglob(f"*{ext}"))

        return [str(f) for f in audio_files]
