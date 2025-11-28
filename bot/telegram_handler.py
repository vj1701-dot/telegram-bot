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
                        file_path: str, max_retries: int = 3) -> bool:
        """
        Send audio file to Telegram with retry logic.
        Converts MP3 to OGG OPUS format first.
        Retries up to max_retries times with 300 second timeout per attempt.
        """
        if bot_token not in self.bots:
            logger.error(f"Bot not found: {bot_token[:20]}...")
            return False

        # Validate file exists
        if not self.file_validator.verify_file(file_path):
            error_msg = f"File not found or invalid: {file_path}"
            logger.error(error_msg)
            self.state_manager.set_last_error(bot_token, error_msg)
            return False

        # Convert to OGG if needed (do this once, outside retry loop)
        try:
            logger.info(f"Processing audio file: {file_path}")
            ogg_path = await self.audio_converter.convert_to_ogg(file_path)
        except Exception as e:
            error_msg = f"Failed to convert audio: {e}"
            logger.error(error_msg)
            self.state_manager.set_last_error(bot_token, str(e))
            return False

        # Retry loop for sending
        for attempt in range(1, max_retries + 1):
            try:
                bot = self.bots[bot_token]

                # Send as voice message with simple caption (date + filename)
                from datetime import datetime
                today_date = datetime.now().strftime("%Y-%m-%d")
                filename = Path(file_path).name

                logger.info(f"Sending (attempt {attempt}/{max_retries}): {filename}")

                with open(ogg_path, 'rb') as audio_file:
                    # Set longer timeout (300 seconds for both read and connect)
                    message = await asyncio.wait_for(
                        bot.send_voice(
                            chat_id=chat_id,
                            voice=audio_file,
                            caption=f"{today_date} {filename}",
                            read_timeout=300,
                            write_timeout=300,
                            connect_timeout=300
                        ),
                        timeout=300
                    )

                logger.info(f"✓ Audio sent: {file_path} to {chat_id}")

                # Update state
                self.state_manager.set_last_sent_file(bot_token, file_path)
                self.state_manager.set_last_run(bot_token)
                self.state_manager.clear_error(bot_token)

                return True

            except asyncio.TimeoutError:
                error_msg = f"Timeout on attempt {attempt}/{max_retries}: {file_path}"
                logger.warning(error_msg)
                if attempt < max_retries:
                    logger.info(f"Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"All {max_retries} attempts failed for: {file_path}")
                    self.state_manager.set_last_error(bot_token, "Timeout after all retries")
                    return False

            except Exception as e:
                error_msg = f"Error on attempt {attempt}/{max_retries}: {e}"
                logger.warning(error_msg)
                if attempt < max_retries:
                    logger.info(f"Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"All {max_retries} attempts failed: {e}")
                    self.state_manager.set_last_error(bot_token, str(e))
                    return False

        return False

    async def send_multiple_audio(self, bot_token: str, chat_id: str,
                                  file_paths: List[str]) -> int:
        """
        Send multiple audio files sequentially in the exact order provided.
        Each file is sent one at a time with retry logic.
        Returns count of successful sends.
        """
        success_count = 0
        total = len(file_paths)

        for index, file_path in enumerate(file_paths, 1):
            logger.info(f"Processing file {index}/{total} in sequence")
            if await self.send_audio(bot_token, chat_id, file_path):
                success_count += 1
                # Small delay between successful sends to avoid rate limiting
                if index < total:  # Don't delay after the last file
                    await asyncio.sleep(2)
            else:
                # Even if a file fails after all retries, continue with the next file
                logger.warning(f"Skipping failed file {index}/{total}, continuing with sequence")

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
