"""Pydantic models for data validation."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from pathlib import Path


class ScheduleEntry(BaseModel):
    """Excel schedule entry."""
    date: str
    path: str
    track_name: str
    enabled: bool = True

    def build_full_path(self) -> str:
        """Build full file path from data directory, path, and track name."""
        data_dir = Path("/app/data")
        return str(data_dir / self.path / self.track_name)


class BotState(BaseModel):
    """Bot runtime state."""
    bot_token: str
    chat_id: Optional[str] = None
    last_run: Optional[str] = None
    last_sent_file: Optional[str] = None
    last_error: str = ""


class AudioFile(BaseModel):
    """Audio file metadata."""
    path: str
    size_bytes: int
    format: str
    duration_seconds: Optional[float] = None


class BotConfig(BaseModel):
    """Bot configuration."""
    bot_token: str
    chat_id: str
    scheduler_time: str = "09:00"
    enabled: bool = True
    created_at: Optional[str] = None
