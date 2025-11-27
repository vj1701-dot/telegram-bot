"""Bot state persistence."""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class BotStateManager:
    """Manages persistent bot state (last run, errors, etc)."""

    def __init__(self, data_dir: Path = Path("/app/data")):
        self.state_file = data_dir / "bot_state.json"
        self.states = self._load_states()

    def _load_states(self) -> dict:
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                return {}
        return {}

    def get_state(self, bot_token: str) -> dict:
        """Get state for specific bot."""
        return self.states.get(bot_token, self._default_state())

    def update_state(self, bot_token: str, **kwargs):
        """Update bot state."""
        if bot_token not in self.states:
            self.states[bot_token] = self._default_state()

        self.states[bot_token].update(kwargs)
        self._save_states()

    def set_last_run(self, bot_token: str):
        """Set last run timestamp."""
        self.update_state(bot_token, last_run=self._now())

    def set_last_sent_file(self, bot_token: str, file_path: str):
        """Set last sent file."""
        self.update_state(bot_token, last_sent_file=file_path)

    def set_last_error(self, bot_token: str, error: str):
        """Set last error."""
        self.update_state(bot_token, last_error=error)

    def clear_error(self, bot_token: str):
        """Clear last error."""
        self.update_state(bot_token, last_error="")

    def _save_states(self):
        """Save state to file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.states, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    @staticmethod
    def _default_state() -> dict:
        """Get default state structure."""
        return {
            "last_run": None,
            "last_sent_file": None,
            "last_error": ""
        }

    @staticmethod
    def _now() -> str:
        """Get current timestamp."""
        return datetime.utcnow().isoformat()
