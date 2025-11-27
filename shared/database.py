"""Persistent configuration storage utilities."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class JSONDatabase:
    """Simple JSON-based persistent storage."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load data from JSON file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded data from {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load {self.file_path}: {e}")
                self.data = {}
        else:
            logger.info(f"No existing data file at {self.file_path}, starting fresh")

    def save(self) -> None:
        """Save data to JSON file."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            logger.debug(f"Saved data to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save {self.file_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value for key."""
        self.data[key] = value
        self.save()

    def delete(self, key: str) -> None:
        """Delete key."""
        if key in self.data:
            del self.data[key]
            self.save()

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.data

    def clear(self) -> None:
        """Clear all data."""
        self.data = {}
        self.save()
