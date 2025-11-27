"""
Configuration management for the bot.
Loads from environment variables and config.json
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, List
from pydantic_settings import BaseSettings
from pydantic import Field
from datetime import datetime


class BotSettings(BaseSettings):
    """Bot configuration from environment and .env file."""

    # Core settings
    data_dir: Path = Field(default=Path("/app/data"))
    log_level: str = Field(default="INFO", env="BOT_LOG_LEVEL")

    # API settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    # Timezone
    timezone: str = Field(default="UTC", env="TZ")

    class Config:
        env_file = "/app/data/.env"
        case_sensitive = False


class BotConfigManager:
    """Manages persistent bot configuration (config.json)."""

    def __init__(self, data_dir: Path = Path("/app/data")):
        self.data_dir = data_dir
        self.config_file = self.data_dir / "config.json"
        self.data = self._load_config()

    def _load_config(self) -> Dict:
        """Load config from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._create_default_config()
        return self._create_default_config()

    def _create_default_config(self) -> Dict:
        """Create default configuration structure."""
        return {
            "bots": [],  # List of bot configs
            "global_timezone": "UTC",
            "default_upload_subfolder": "",
            "theme": "light"
        }

    def add_bot(self, bot_token: str, chat_id: str,
                scheduler_time: str = "09:00") -> bool:
        """Add new bot configuration."""
        if any(b["bot_token"] == bot_token for b in self.data["bots"]):
            return False

        self.data["bots"].append({
            "bot_token": bot_token,
            "chat_id": chat_id,
            "scheduler_time": scheduler_time,
            "enabled": True,
            "created_at": self._now()
        })
        self.save()
        return True

    def update_bot(self, bot_token: str, **kwargs):
        """Update existing bot configuration."""
        for bot in self.data["bots"]:
            if bot["bot_token"] == bot_token:
                bot.update(kwargs)
                self.save()
                return True
        return False

    def delete_bot(self, bot_token: str):
        """Delete bot configuration."""
        self.data["bots"] = [b for b in self.data["bots"]
                             if b["bot_token"] != bot_token]
        self.save()

    def get_bots(self) -> List[Dict]:
        """Get all bot configurations."""
        return self.data.get("bots", [])

    def get_bot(self, bot_token: str) -> Optional[Dict]:
        """Get specific bot configuration."""
        for bot in self.data["bots"]:
            if bot["bot_token"] == bot_token:
                return bot
        return None

    def save(self):
        """Save configuration to file."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    @staticmethod
    def _now() -> str:
        """Current timestamp."""
        return datetime.utcnow().isoformat()


def get_settings() -> BotSettings:
    """Get application settings (singleton)."""
    return BotSettings()
