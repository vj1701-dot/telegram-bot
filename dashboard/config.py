"""Dashboard configuration."""
import os
from pathlib import Path


class DashboardConfig:
    """Configuration for Streamlit dashboard."""

    BOT_API_URL = os.getenv("BOT_API_URL", "http://localhost:8000")
    DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
    REFRESH_INTERVAL = 5  # seconds
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

    # Theme colors
    PRIMARY_COLOR = "#FF6B6B"
    SECONDARY_COLOR = "#4ECDC4"

    # Supported audio formats
    AUDIO_FORMATS = ["mp3", "ogg", "wav", "m4a"]
