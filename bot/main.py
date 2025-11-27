"""
Main entry point for Telegram Audio Bot container.
Initializes scheduler, bot, and API server.
"""
import asyncio
import logging
import sys
from pathlib import Path

from bot.telegram_handler import TelegramBotManager
from bot.scheduler import SchedulerManager
from bot.api_server import create_app
from bot.logger import setup_logger
from bot.config import get_settings
import uvicorn

# Setup logging
logger = setup_logger("bot", level="INFO")


class BotApplicationManager:
    """Manages bot lifecycle: initialization, running, shutdown."""

    def __init__(self):
        self.bot_manager = None
        self.scheduler_manager = None
        self.app = None
        self.settings = get_settings()

    async def initialize(self):
        """Initialize all components."""
        logger.info("=" * 60)
        logger.info("Telegram Audio Bot - Starting Initialization")
        logger.info("=" * 60)

        # Initialize bot manager
        logger.info("Initializing Telegram Bot Manager...")
        self.bot_manager = TelegramBotManager()
        await self.bot_manager.initialize()

        # Initialize scheduler
        logger.info("Initializing Scheduler Manager...")
        self.scheduler_manager = SchedulerManager()
        self.scheduler_manager.initialize(self.bot_manager)

        # Create FastAPI app
        logger.info("Creating FastAPI application...")
        self.app = create_app(self.bot_manager, self.scheduler_manager)

        logger.info("✓ All components initialized successfully")

    async def start_api(self):
        """Start FastAPI server (non-blocking)."""
        logger.info(f"Starting API server on {self.settings.api_host}:{self.settings.api_port}")

        config = uvicorn.Config(
            self.app,
            host=self.settings.api_host,
            port=self.settings.api_port,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)

        # Run server in background
        asyncio.create_task(server.serve())

        logger.info(f"✓ API server started at http://{self.settings.api_host}:{self.settings.api_port}")

    async def run(self):
        """Main run loop."""
        try:
            await self.initialize()
            await self.start_api()

            logger.info("=" * 60)
            logger.info("Bot application is running")
            logger.info("Web UI: http://localhost:8000")
            logger.info("API Docs: http://localhost:8000/docs")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 60)

            # Keep alive - no polling needed for send-only bot
            while True:
                await asyncio.sleep(3600)  # Sleep 1 hour, scheduler handles sending

        except Exception as e:
            logger.error(f"Fatal error in run loop: {e}", exc_info=True)
            raise

    def shutdown(self):
        """Shutdown all components gracefully."""
        logger.info("Shutting down bot application...")

        if self.scheduler_manager:
            self.scheduler_manager.shutdown()

        logger.info("✓ Shutdown complete")


async def main():
    """Application entry point."""
    manager = BotApplicationManager()

    try:
        await manager.run()
    except KeyboardInterrupt:
        logger.info("\nShutdown signal received (Ctrl+C)")
        manager.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        manager.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
