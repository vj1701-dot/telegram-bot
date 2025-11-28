"""
Daily scheduler for sending audio files.
Uses APScheduler for cron-like scheduling.
"""
import logging
from typing import Optional
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from pathlib import Path

from bot.utils.excel_parser import ExcelParser
from bot.config import BotConfigManager
from shared.models import ScheduleEntry

logger = logging.getLogger(__name__)


class SchedulerManager:
    """
    Manages scheduled audio sending.
    Reads schedule from Excel and sends at configured times.
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.bot_manager = None
        self.excel_parser = ExcelParser()

    def initialize(self, bot_manager):
        """Initialize with bot manager reference."""
        self.bot_manager = bot_manager
        self._load_schedules()
        self.scheduler.start()
        logger.info("Scheduler initialized and started")

    def _load_schedules(self):
        """Load schedules from config and set up cron jobs."""
        config_manager = BotConfigManager(Path("/app/data"))
        bots = config_manager.get_bots()

        logger.info(f"Loading schedules for {len(bots)} bot(s)...")

        for bot_config in bots:
            if bot_config.get("enabled"):
                time_parts = bot_config["scheduler_time"].split(":")
                hour, minute = int(time_parts[0]), int(time_parts[1])

                job_id = f"schedule_{bot_config['bot_token'][:20]}"

                # Remove existing job if present
                try:
                    self.scheduler.remove_job(job_id)
                    logger.info(f"Removed existing job: {job_id}")
                except:
                    pass

                # Add daily trigger
                tz = self._get_timezone(config_manager)
                trigger = CronTrigger(hour=hour, minute=minute, timezone=tz)

                # Get schedules for this bot (default to schedule.xlsx if not set)
                bot_schedules = bot_config.get("schedules", ["schedule.xlsx"])

                self.scheduler.add_job(
                    self._run_daily_schedule,
                    trigger=trigger,
                    id=job_id,
                    args=[bot_config["bot_token"], bot_config["chat_id"], bot_schedules],
                    name=f"Daily schedule for bot {bot_config['bot_token'][:20]}..."
                )

                logger.info(f"✓ Scheduled job: {job_id} at {hour:02d}:{minute:02d} ({tz}) with schedules: {', '.join(bot_schedules)}")

    async def _run_daily_schedule(self, bot_token: str, chat_id: str, schedules: list = None):
        """Execute daily schedule for specific bot.

        Files are sent in the order determined by the schedules list.
        For example, if schedules = ['morning.csv', 'evening.csv']:
        - All files from morning.csv (for today) are sent first
        - Then all files from evening.csv (for today) are sent
        This allows precise control over send order.
        """
        logger.info(f"Running daily schedule for bot: {bot_token[:20]}...")

        try:
            # Parse today's schedule from specified schedule files (in order)
            if schedules is None:
                schedules = ["schedule.xlsx"]

            schedule_entries = self.excel_parser.get_today_entries_from_files(schedules)

            if not schedule_entries:
                logger.info("No entries scheduled for today")
                return

            logger.info(f"Found {len(schedule_entries)} entries for today from schedules: {', '.join(schedules)}")

            # Send each audio file in the order returned
            success_count = 0
            for entry in schedule_entries:
                file_path = entry.build_full_path()
                logger.info(f"Sending: {file_path}")

                if await self.bot_manager.send_audio(bot_token, chat_id, file_path):
                    success_count += 1
                else:
                    logger.warning(f"Failed to send: {file_path}")

            logger.info(f"Daily schedule complete: {success_count}/{len(schedule_entries)} sent successfully")

        except Exception as e:
            logger.error(f"Schedule execution failed: {e}", exc_info=True)

    async def send_by_date(self, bot_token: str, chat_id: str, date_str: str, schedules: list = None) -> int:
        """
        Send all audio files for a specific date from specific schedule files.
        Maintains the order of schedules list.
        Returns count of successful sends.
        """
        try:
            if schedules is None:
                # Fallback to all schedules if not specified
                entries = self.excel_parser.get_entries_by_date(date_str)
            else:
                # Use specific schedules in the order provided
                entries = self.excel_parser.get_entries_by_date_from_files(date_str, schedules)

            if not entries:
                logger.info(f"No entries found for date: {date_str}")
                return 0

            logger.info(f"Sending {len(entries)} entries for {date_str} from schedules: {', '.join(schedules or ['all'])}")

            file_paths = [entry.build_full_path() for entry in entries]
            success_count = await self.bot_manager.send_multiple_audio(
                bot_token, chat_id, file_paths
            )

            return success_count

        except Exception as e:
            logger.error(f"Failed to send by date: {e}")
            return 0

    async def resend_audio(self, bot_token: str, chat_id: str, file_path: str) -> bool:
        """Manual resend of audio file."""
        try:
            return await self.bot_manager.send_audio(bot_token, chat_id, file_path)
        except Exception as e:
            logger.error(f"Manual resend failed: {e}")
            return False

    def reload_schedules(self):
        """Reload all schedules from config."""
        logger.info("Reloading schedules...")
        self._load_schedules()
        logger.info("Schedules reloaded successfully")

    def get_jobs(self) -> list:
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()

    def _get_timezone(self, config_manager: BotConfigManager):
        """Get timezone for bot."""
        tz_name = config_manager.data.get("global_timezone", "UTC")
        return pytz.timezone(tz_name)

    def shutdown(self):
        """Shutdown scheduler gracefully."""
        logger.info("Shutting down scheduler...")
        self.scheduler.shutdown()
