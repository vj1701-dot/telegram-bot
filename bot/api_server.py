"""
FastAPI server for dashboard communication.
Provides endpoints for bot control and diagnostics.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SendAudioRequest(BaseModel):
    """Request model for sending audio."""
    bot_token: str
    chat_id: str
    file_path: str


class SendByDateRequest(BaseModel):
    """Request model for sending by date."""
    bot_token: str
    chat_id: str
    date: str


class BotStatusResponse(BaseModel):
    """Response model for bot status."""
    bot_token: str
    chat_id: Optional[str] = None
    last_run: Optional[str] = None
    last_sent_file: Optional[str] = None
    last_error: str = ""
    is_healthy: bool = True


def create_app(bot_manager, scheduler_manager) -> FastAPI:
    """Create FastAPI application with routes."""
    app = FastAPI(
        title="Telegram Audio Bot API",
        description="API for managing Telegram audio bot and scheduled sends",
        version="1.0.0"
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "telegram-audio-bot",
            "version": "1.0.0"
        }

    @app.post("/send-audio")
    async def send_audio(request: SendAudioRequest):
        """Manually send audio file."""
        logger.info(f"API: Send audio request for {request.file_path}")

        success = await bot_manager.send_audio(
            request.bot_token,
            request.chat_id,
            request.file_path
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to send audio")

        return {
            "status": "sent",
            "file_path": request.file_path
        }

    @app.post("/send-by-date")
    async def send_by_date(request: SendByDateRequest):
        """Send all audio files for a specific date."""
        logger.info(f"API: Send by date request for {request.date}")

        success_count = await scheduler_manager.send_by_date(
            request.bot_token,
            request.chat_id,
            request.date
        )

        return {
            "status": "completed",
            "date": request.date,
            "success_count": success_count
        }

    @app.post("/resend-audio")
    async def resend_audio(bot_token: str, chat_id: str, file_path: str):
        """Resend specific audio file."""
        logger.info(f"API: Resend audio request for {file_path}")

        success = await scheduler_manager.resend_audio(bot_token, chat_id, file_path)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to resend audio")

        return {
            "status": "resent",
            "file_path": file_path
        }

    @app.get("/bot-status/{bot_token}", response_model=BotStatusResponse)
    async def get_bot_status(bot_token: str):
        """Get bot diagnostics for specific bot."""
        state = bot_manager.get_bot_state(bot_token)

        if not state:
            raise HTTPException(status_code=404, detail="Bot not found")

        return BotStatusResponse(
            bot_token=bot_token,
            chat_id=state.get("chat_id"),
            last_run=state.get("last_run"),
            last_sent_file=state.get("last_sent_file"),
            last_error=state.get("last_error", ""),
            is_healthy=state.get("last_error", "") == ""
        )

    @app.get("/bot-status-all", response_model=List[BotStatusResponse])
    async def get_all_bot_status():
        """Get status for all bots."""
        states = bot_manager.get_all_bot_states()

        return [
            BotStatusResponse(
                bot_token=token,
                chat_id=state.get("chat_id"),
                last_run=state.get("last_run"),
                last_sent_file=state.get("last_sent_file"),
                last_error=state.get("last_error", ""),
                is_healthy=state.get("last_error", "") == ""
            )
            for token, state in states.items()
        ]

    @app.post("/reload-config")
    async def reload_configuration():
        """Reload configuration and restart scheduler."""
        logger.info("API: Reload config request")

        try:
            # Reinitialize bot manager
            await bot_manager.initialize()

            # Reload scheduler
            scheduler_manager.reload_schedules()

            return {"status": "reloaded"}
        except Exception as e:
            logger.error(f"Failed to reload config: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/scheduler-jobs")
    async def get_scheduler_jobs():
        """Get all scheduled jobs."""
        jobs = scheduler_manager.get_jobs()

        return {
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else None
                }
                for job in jobs
            ]
        }

    @app.post("/test-connection")
    async def test_connection(bot_token: str):
        """Test bot connection to Telegram API."""
        success = await bot_manager.test_bot_connection(bot_token)

        if not success:
            raise HTTPException(status_code=400, detail="Connection test failed")

        return {"status": "connected"}

    return app
