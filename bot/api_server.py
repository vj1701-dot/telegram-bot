"""
FastAPI server for dashboard communication.
Provides endpoints for bot control and diagnostics.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import logging
import shutil

logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path("/app/data")


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

    # Serve HTML UI
    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        """Serve the HTML UI."""
        html_path = Path(__file__).parent / "web" / "templates" / "index.html"
        if html_path.exists():
            return html_path.read_text()
        return "<h1>Telegram Audio Bot</h1><p>UI not found. Visit <a href='/docs'>/docs</a> for API.</p>"

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

    # New endpoints for HTML UI
    @app.get("/api/status")
    async def get_status():
        """Get overall system status."""
        from bot.config import BotConfigManager
        config_mgr = BotConfigManager(DATA_DIR)
        bots = config_mgr.get_bots()

        schedule_file = DATA_DIR / "schedule.xlsx"

        # Count audio files
        audio_dir = DATA_DIR / "audio"
        file_count = 0
        if audio_dir.exists():
            file_count = len(list(audio_dir.rglob("*.mp3"))) + \
                        len(list(audio_dir.rglob("*.ogg"))) + \
                        len(list(audio_dir.rglob("*.opus"))) + \
                        len(list(audio_dir.rglob("*.wav"))) + \
                        len(list(audio_dir.rglob("*.m4a")))

        return {
            "bot_count": len([b for b in bots if b.get("enabled")]),
            "schedule_exists": schedule_file.exists(),
            "file_count": file_count
        }

    @app.get("/api/bots")
    async def get_bots():
        """Get all configured bots."""
        from bot.config import BotConfigManager
        config_mgr = BotConfigManager(DATA_DIR)
        return config_mgr.get_bots()

    @app.post("/api/bots")
    async def add_bot(
        bot_token: str = Form(...),
        chat_id: str = Form(...),
        scheduler_time: str = Form("09:00"),
        schedules: str = Form("[]")
    ):
        """Add a new bot."""
        from bot.config import BotConfigManager
        import json

        config_mgr = BotConfigManager(DATA_DIR)

        # Parse schedules JSON
        try:
            schedules_list = json.loads(schedules) if schedules else []
        except json.JSONDecodeError:
            schedules_list = []

        if config_mgr.add_bot(bot_token, chat_id, scheduler_time, schedules_list):
            # Reload config
            await bot_manager.initialize()
            scheduler_manager.reload_schedules()
            return {"status": "added"}
        else:
            raise HTTPException(status_code=400, detail="Bot already exists")

    @app.put("/api/bots/{bot_token}")
    async def update_bot(
        bot_token: str,
        chat_id: str = Form(...),
        scheduler_time: str = Form(...),
        enabled: bool = Form(...),
        schedules: str = Form("[]")
    ):
        """Update an existing bot configuration."""
        from bot.config import BotConfigManager
        import json

        config_mgr = BotConfigManager(DATA_DIR)

        # Parse schedules JSON
        try:
            schedules_list = json.loads(schedules) if schedules else []
        except json.JSONDecodeError:
            schedules_list = []

        updated = config_mgr.update_bot(
            bot_token,
            chat_id=chat_id,
            scheduler_time=scheduler_time,
            enabled=enabled,
            schedules=schedules_list
        )

        if updated:
            # Reload config
            await bot_manager.initialize()
            scheduler_manager.reload_schedules()
            return {"status": "updated"}
        else:
            raise HTTPException(status_code=404, detail="Bot not found")

    @app.delete("/api/bots/{bot_token}")
    async def delete_bot(bot_token: str):
        """Delete a bot configuration."""
        from bot.config import BotConfigManager
        config_mgr = BotConfigManager(DATA_DIR)

        config_mgr.delete_bot(bot_token)

        # Reload config
        await bot_manager.initialize()
        scheduler_manager.reload_schedules()

        return {"status": "deleted"}

    @app.post("/api/upload")
    async def upload_file(file: UploadFile = File(...), folder: str = Form("audio/")):
        """Upload audio file."""
        target_dir = DATA_DIR / folder
        target_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"status": "uploaded", "filename": file.filename}

    @app.post("/api/schedule")
    async def upload_schedule(file: UploadFile = File(...)):
        """Upload schedule file (.xlsx, .ods, or .csv)."""
        allowed_extensions = {'.xlsx', '.ods', '.csv'}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Only {', '.join(allowed_extensions)} files allowed"
            )

        schedule_path = DATA_DIR / file.filename

        with open(schedule_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"status": "uploaded", "filename": file.filename}

    @app.get("/api/schedule")
    async def download_schedule():
        """Download schedule.xlsx file."""
        schedule_path = DATA_DIR / "schedule.xlsx"

        if not schedule_path.exists():
            raise HTTPException(status_code=404, detail="Schedule file not found")

        return FileResponse(schedule_path, filename="schedule.xlsx")

    @app.get("/api/schedules/list")
    async def list_schedules():
        """List all schedule files (.xlsx, .ods, .csv)."""
        schedule_files = []
        for pattern in ["schedule*.xlsx", "schedule*.ods", "schedule*.csv"]:
            schedule_files.extend(list(DATA_DIR.glob(pattern)))

        # Also check schedules subfolder
        schedules_dir = DATA_DIR / "schedules"
        if schedules_dir.exists():
            for ext in ["*.xlsx", "*.ods", "*.csv"]:
                schedule_files.extend(list(schedules_dir.glob(ext)))

        files = [f.name for f in schedule_files]
        return {"schedules": files}

    @app.get("/api/schedule/data")
    async def get_schedule_data(filename: str = "schedule.xlsx"):
        """Get schedule data as JSON for editing."""
        import pandas as pd

        # Try main data dir first, then schedules subfolder
        schedule_path = DATA_DIR / filename
        if not schedule_path.exists():
            schedule_path = DATA_DIR / "schedules" / filename

        if not schedule_path.exists():
            return {"rows": []}

        try:
            # Read based on file extension
            file_ext = schedule_path.suffix.lower()
            if file_ext == '.csv':
                df = pd.read_csv(schedule_path)
            elif file_ext == '.ods':
                df = pd.read_excel(schedule_path, engine='odf')
            else:  # .xlsx
                df = pd.read_excel(schedule_path)

            rows = df.to_dict('records')
            return {"rows": rows, "filename": filename}
        except Exception as e:
            logger.error(f"Failed to read schedule file {filename}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read schedule file: {str(e)}"
            )

    @app.post("/api/schedule/data")
    async def save_schedule_data(rows: str = Form(...), filename: str = Form("schedule.xlsx")):
        """Save schedule data from JSON."""
        import pandas as pd
        import json
        from datetime import datetime

        # Determine save location
        schedule_path = DATA_DIR / filename

        try:
            # Parse the JSON string
            rows_data = json.loads(rows)

            if not rows_data:
                # Empty schedule
                df = pd.DataFrame(columns=['Date', 'Path', 'Track Name', 'Enabled'])
            else:
                # Create DataFrame
                df = pd.DataFrame(rows_data)

                # Convert date strings to proper format
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

                # Ensure boolean for Enabled
                if 'Enabled' in df.columns:
                    df['Enabled'] = df['Enabled'].astype(bool)

                # Ensure correct column order
                expected_cols = ['Date', 'Path', 'Track Name', 'Enabled']
                df = df[expected_cols]

            # Save based on file extension
            file_ext = schedule_path.suffix.lower()
            if file_ext == '.csv':
                df.to_csv(schedule_path, index=False)
            elif file_ext == '.ods':
                df.to_excel(schedule_path, index=False, engine='odf')
            else:  # .xlsx
                df.to_excel(schedule_path, index=False, engine='openpyxl')

            logger.info(f"Schedule saved successfully: {filename} with {len(rows_data)} rows")
            return {"status": "saved", "rows": len(rows_data), "filename": filename}

        except Exception as e:
            logger.error(f"Failed to save schedule: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to save schedule: {str(e)}")

    @app.post("/api/schedule/create")
    async def create_schedule(filename: str = Form(...)):
        """Create a new empty schedule file (.xlsx, .ods, or .csv)."""
        import pandas as pd

        # Sanitize filename
        filename = filename.strip()

        # Check if filename has a valid extension, add .xlsx if not
        file_ext = Path(filename).suffix.lower()
        allowed_extensions = {'.xlsx', '.ods', '.csv'}
        if file_ext not in allowed_extensions:
            filename += '.xlsx'
            file_ext = '.xlsx'

        schedule_path = DATA_DIR / filename

        if schedule_path.exists():
            raise HTTPException(status_code=400, detail="Schedule already exists")

        # Create empty schedule
        df = pd.DataFrame(columns=['Date', 'Path', 'Track Name', 'Enabled'])

        # Save based on file extension
        if file_ext == '.csv':
            df.to_csv(schedule_path, index=False)
        elif file_ext == '.ods':
            df.to_excel(schedule_path, index=False, engine='odf')
        else:  # .xlsx
            df.to_excel(schedule_path, index=False, engine='openpyxl')

        logger.info(f"Created new schedule: {filename}")
        return {"status": "created", "filename": filename}

    @app.delete("/api/schedule/delete")
    async def delete_schedule(filename: str = Form(...)):
        """Delete a schedule file."""
        if filename == "schedule.xlsx":
            raise HTTPException(status_code=400, detail="Cannot delete default schedule")

        schedule_path = DATA_DIR / filename

        if not schedule_path.exists():
            raise HTTPException(status_code=404, detail="Schedule not found")

        schedule_path.unlink()
        logger.info(f"Deleted schedule: {filename}")
        return {"status": "deleted", "filename": filename}

    @app.post("/api/send-manual")
    async def send_manual(date: str = Form(...)):
        """Manually send audio for a specific date."""
        from bot.config import BotConfigManager
        config_mgr = BotConfigManager(DATA_DIR)
        bots = config_mgr.get_bots()

        total_sent = 0
        for bot_config in bots:
            if bot_config.get("enabled"):
                count = await scheduler_manager.send_by_date(
                    bot_config["bot_token"],
                    bot_config["chat_id"],
                    date
                )
                total_sent += count

        return {"status": "sent", "count": total_sent, "date": date}

    return app
