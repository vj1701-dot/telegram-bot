"""Tests for configuration management."""
import pytest
from pathlib import Path
import json
from bot.config import BotConfigManager


class TestBotConfigManager:
    """Test bot configuration management."""

    def test_creates_default_config(self, tmp_path):
        """Test that default config is created."""
        config_mgr = BotConfigManager(tmp_path)

        assert "bots" in config_mgr.data
        assert "global_timezone" in config_mgr.data
        assert config_mgr.data["global_timezone"] == "UTC"

    def test_add_bot(self, tmp_path):
        """Test adding a bot."""
        config_mgr = BotConfigManager(tmp_path)

        success = config_mgr.add_bot(
            bot_token="test_token_123",
            chat_id="test_chat_456",
            scheduler_time="09:00"
        )

        assert success is True
        assert len(config_mgr.get_bots()) == 1

        bot = config_mgr.get_bots()[0]
        assert bot["bot_token"] == "test_token_123"
        assert bot["chat_id"] == "test_chat_456"
        assert bot["scheduler_time"] == "09:00"
        assert bot["enabled"] is True

    def test_add_duplicate_bot_fails(self, tmp_path):
        """Test that adding duplicate bot token fails."""
        config_mgr = BotConfigManager(tmp_path)

        config_mgr.add_bot("token1", "chat1")
        success = config_mgr.add_bot("token1", "chat2")

        assert success is False
        assert len(config_mgr.get_bots()) == 1

    def test_update_bot(self, tmp_path):
        """Test updating bot configuration."""
        config_mgr = BotConfigManager(tmp_path)

        config_mgr.add_bot("token1", "chat1", "09:00")
        config_mgr.update_bot("token1", scheduler_time="10:00", enabled=False)

        bot = config_mgr.get_bot("token1")
        assert bot["scheduler_time"] == "10:00"
        assert bot["enabled"] is False

    def test_delete_bot(self, tmp_path):
        """Test deleting bot configuration."""
        config_mgr = BotConfigManager(tmp_path)

        config_mgr.add_bot("token1", "chat1")
        config_mgr.add_bot("token2", "chat2")

        config_mgr.delete_bot("token1")

        assert len(config_mgr.get_bots()) == 1
        assert config_mgr.get_bot("token1") is None
        assert config_mgr.get_bot("token2") is not None

    def test_config_persists(self, tmp_path):
        """Test that config persists to file."""
        config_mgr = BotConfigManager(tmp_path)
        config_mgr.add_bot("token1", "chat1")

        # Create new instance and verify data persists
        new_config_mgr = BotConfigManager(tmp_path)
        assert len(new_config_mgr.get_bots()) == 1
