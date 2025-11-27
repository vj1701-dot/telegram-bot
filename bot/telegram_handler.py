"""
Telegram bot initialization and message handlers.
Manages multiple bot instances (one per token).
"""
import logging
from typing import Dict, List, Optional
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from pathlib import Path

from bot.utils.audio_converter import AudioConverter
from bot.utils.file_validator import FileValidator
from bot.utils.excel_parser import ExcelParser
from bot.utils.bot_state import BotStateManager
from bot.config import BotConfigManager
from shared.models import BotState

logger = logging.getLogger(__name__)


class TelegramBotManager:
    """
    Manages multiple Telegram bot instances.
    One bot per BOT_TOKEN.
    """

    def __init__(self):
        self.bots: Dict[str, Bot] = {}
        self.bot_states: Dict[str, dict] = {}
        self.audio_converter = AudioConverter()
        self.file_validator = FileValidator()
        self.excel_parser = ExcelParser()
        self.state_manager = BotStateManager()

    async def initialize(self):
        """Initialize all bot instances from config."""
        config_manager = BotConfigManager(Path("/app/data"))
        bots_config = config_manager.get_bots()

        logger.info(f"Initializing {len(bots_config)} bot(s)...")

        for bot_config in bots_config:
            if bot_config.get("enabled"):
                await self._add_bot(bot_config["bot_token"], bot_config["chat_id"])

    async def _add_bot(self, bot_token: str, chat_id: str):
        """Create and test bot instance."""
        try:
            bot = Bot(token=bot_token)
            # Test connection
            user = await bot.get_me()
            self.bots[bot_token] = bot
            self.bot_states[bot_token] = self.state_manager.get_state(bot_token)
            self.bot_states[bot_token]["chat_id"] = chat_id
            logger.info(f"Bot initialized: {user.username} (ID: {user.id})")
        except TelegramError as e:
            logger.error(f"Failed to initialize bot: {e}")
            self.state_manager.set_last_error(bot_token, str(e))

    async def send_audio(self, bot_token: str, chat_id: str,
                        file_path: str) -> bool:
        """
        Send audio file to Telegram.
        Converts MP3 to OGG OPUS format first.
        """
        if bot_token not in self.bots:
            logger.error(f"Bot not found: {bot_token[:20]}...")
            return False

        try:
            bot = self.bots[bot_token]

            # Validate file exists
            if not self.file_validator.verify_file(file_path):
                error_msg = f"File not found or invalid: {file_path}"
                logger.error(error_msg)
                self.state_manager.set_last_error(bot_token, error_msg)
                return False

            # Convert to OGG if needed
            logger.info(f"Processing audio file: {file_path}")
            ogg_path = await self.audio_converter.convert_to_ogg(file_path)

            # Send as voice message
            with open(ogg_path, 'rb') as audio_file:
                message = await bot.send_voice(
                    chat_id=chat_id,
                    voice=audio_file,
                    caption=f"📻 Scheduled: {Path(file_path).name}"
                )

            logger.info(f"✓ Audio sent: {file_path} to {chat_id}")

            # Update state
            self.state_manager.set_last_sent_file(bot_token, file_path)
            self.state_manager.set_last_run(bot_token)
            self.state_manager.clear_error(bot_token)

            return True

        except Exception as e:
            error_msg = f"Failed to send audio: {e}"
            logger.error(error_msg)
            self.state_manager.set_last_error(bot_token, str(e))
            return False

    async def send_multiple_audio(self, bot_token: str, chat_id: str,
                                  file_paths: List[str]) -> int:
        """Send multiple audio files. Returns count of successful sends."""
        success_count = 0
        for file_path in file_paths:
            if await self.send_audio(bot_token, chat_id, file_path):
                success_count += 1
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
        return success_count

    async def test_bot_connection(self, bot_token: str) -> bool:
        """Test if bot can connect to Telegram API."""
        try:
            bot = Bot(token=bot_token)
            user = await bot.get_me()
            logger.info(f"Connection test successful: {user.username}")
            return True
        except TelegramError as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_bot_state(self, bot_token: str) -> dict:
        """Get current state for a bot."""
        return self.state_manager.get_state(bot_token)

    def get_all_bot_states(self) -> Dict[str, dict]:
        """Get states for all bots."""
        return self.state_manager.states

    async def start_polling(self):
        """Start polling for updates (if needed for commands)."""
        logger.info("Bot polling mode active (monitoring for updates)")
        # Keep running - can be extended for user commands
        while True:
            await asyncio.sleep(60)
