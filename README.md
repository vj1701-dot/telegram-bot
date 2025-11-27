# Telegram Audio Bot with Streamlit Dashboard

A production-ready multi-container Docker application for scheduled Telegram audio message delivery with real-time management dashboard.

## Features

### Bot Features
- ✅ Support multiple BOT_TOKEN & CHAT_ID pairs
- ✅ Automatic MP3 → OGG OPUS conversion using FFmpeg
- ✅ Daily scheduler with configurable times per bot
- ✅ Manual Send/Resend functionality
- ✅ Full file path construction from Excel schedule
- ✅ Persistent error logging and state management
- ✅ FastAPI endpoint for dashboard communication
- ✅ Timezone-aware scheduling

### Dashboard Features
- **Configuration Tab**: Add/Edit/Delete multiple bot tokens and chat IDs
- **Scheduler Tab**: Set daily trigger times per bot with timezone support
- **Schedule Editor**: View/edit Excel schedule with real-time preview
- **File Management**: Upload audio files, verify schedule references, browse files
- **Manual Send**: Trigger audio sends manually per schedule row or date
- **Diagnostics**: Monitor bot health, last runs, errors, and API status
- **Settings**: Theme toggle, timezone selection, preferences

## Architecture

```
telegram-audio-bot/
├── bot/              # Telegram bot container
│   ├── main.py       # Bot entry point
│   ├── config.py     # Configuration management
│   ├── scheduler.py  # APScheduler for daily sends
│   ├── telegram_handler.py  # Bot management
│   ├── api_server.py # FastAPI endpoints
│   └── utils/        # Audio converter, file validator, Excel parser
├── dashboard/        # Streamlit dashboard container
│   ├── app.py        # Dashboard entry point
│   ├── pages/        # 7 dashboard pages
│   └── components/   # Reusable UI components
├── shared/           # Shared utilities (models, constants, database)
├── data/             # Shared volume (audio files, schedules, logs)
├── docker-compose.yml
└── Dockerfile
```

### Multi-Container Design
- **Bot Container**: Handles Telegram API, scheduling, audio conversion, and provides REST API
- **Dashboard Container**: Streamlit web UI for management and monitoring
- **Shared Volume**: `/data` for Excel schedules, audio files, logs, and configuration

## Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Telegram Chat ID (your channel or group ID)

### Installation

1. **Clone or navigate to project directory:**
```bash
cd "telegram bot"
```

2. **Build and start containers:**
```bash
docker-compose up -d --build
```

3. **Access the dashboard:**
- Streamlit Dashboard: http://localhost:8501
- Bot API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Initial Setup

1. **Configure Your First Bot:**
   - Open dashboard at http://localhost:8501
   - Go to **Configuration** → **Add Bot**
   - Enter Bot Token and Chat ID
   - Test connection
   - Set scheduler time

2. **Create Schedule File:**
   - Go to **Schedule Editor**
   - Click "Create Template Schedule"
   - Edit dates, paths, and track names
   - Save schedule

3. **Upload Audio Files:**
   - Go to **File Management** → **Upload Files**
   - Select target folder
   - Upload MP3/OGG/WAV/M4A files
   - Verify files match schedule

4. **Set Schedule Time:**
   - Go to **Scheduler**
   - Set daily send time for each bot
   - Configure timezone in **Settings**

5. **Monitor:**
   - Go to **Diagnostics**
   - View bot status, logs, and health
   - Enable auto-refresh for real-time monitoring

## File Structure Details

### /data Directory (Shared Volume)

```
data/
├── schedule.xlsx              # Excel schedule
├── config.json                # Bot configurations
├── bot_state.json             # Runtime state
├── .env                       # Optional environment variables
├── logs/
│   ├── bot.log               # Bot activity logs
│   └── scheduler.log         # Scheduler events
├── .audio_cache/             # Converted OGG files (auto-created)
└── audio/                    # Your audio files
    ├── sample.mp3
    ├── news/
    │   └── morning_news.mp3
    └── podcasts/
        └── episode1.mp3
```

### Excel Schedule Format

The `schedule.xlsx` file should have these columns:

| Date       | Path      | Track Name         | Enabled |
|------------|-----------|--------------------|---------|
| 2024-01-15 | audio/    | morning_brief.mp3  | TRUE    |
| 2024-01-15 | audio/news/ | news_update.mp3  | TRUE    |
| 2024-01-16 | audio/    | daily_podcast.mp3  | TRUE    |

**Column Descriptions:**
- **Date**: YYYY-MM-DD format
- **Path**: Relative path from `/data` (e.g., `audio/` or `audio/news/`)
- **Track Name**: Filename with extension
- **Enabled**: TRUE or FALSE (controls whether entry is active)

**Full file path is constructed as:** `/data` + Path + Track Name

## Configuration

### Bot Configuration (config.json)

Automatically created by the dashboard. Located at `/data/config.json`:

```json
{
  "bots": [
    {
      "bot_token": "YOUR_BOT_TOKEN",
      "chat_id": "YOUR_CHAT_ID",
      "scheduler_time": "09:00",
      "enabled": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "global_timezone": "America/New_York",
  "default_upload_subfolder": "audio/",
  "theme": "light"
}
```

### Environment Variables

Create a `.env` file in the `/data` directory (optional):

```env
# Bot Settings
BOT_LOG_LEVEL=INFO
TZ=UTC

# API Settings (usually don't need to change)
BOT_API_URL=http://bot:8000
DATA_DIR=/app/data
```

## API Endpoints

The bot container exposes a FastAPI server for dashboard communication:

### Health Check
```bash
GET /health
# Returns: {"status": "healthy"}
```

### Send Audio
```bash
POST /send-audio
Content-Type: application/json

{
  "bot_token": "your_token",
  "chat_id": "your_chat_id",
  "file_path": "/app/data/audio/sample.mp3"
}
```

### Get Bot Status
```bash
GET /bot-status/{bot_token}
# Returns bot state including last run, last file, errors
```

### Get All Bot Status
```bash
GET /bot-status-all
# Returns status for all configured bots
```

### Send by Date
```bash
POST /send-by-date
Content-Type: application/json

{
  "bot_token": "your_token",
  "chat_id": "your_chat_id",
  "date": "2024-01-15"
}
```

### Reload Configuration
```bash
POST /reload-config
# Reloads config and restarts scheduler
```

### Get Scheduler Jobs
```bash
GET /scheduler-jobs
# Returns all scheduled jobs with next run times
```

## Supported Timezones

All North America timezones are supported. Set in **Settings** → **Timezone**.

Examples:
- `UTC`
- `US/Eastern`, `America/New_York`
- `US/Central`, `America/Chicago`
- `US/Mountain`, `America/Denver`
- `US/Pacific`, `America/Los_Angeles`
- `US/Alaska`, `America/Anchorage`
- `US/Hawaii`, `Pacific/Honolulu`

See `north_america_timezones.txt` for complete list.

## Troubleshooting

### Bot Not Sending Messages

1. **Check bot token validity:**
   - Dashboard → Configuration → Test Connection

2. **Verify chat ID:**
   - Make sure bot is added to the channel/group
   - Use [@userinfobot](https://t.me/userinfobot) to get chat ID

3. **Check logs:**
   ```bash
   docker logs telegram-audio-bot
   # or via Dashboard → Diagnostics → Logs
   ```

4. **Verify file exists:**
   - Dashboard → File Management → Verify Files

### Scheduler Not Running

1. **Check scheduler time format:** Must be HH:MM (24-hour)
2. **Verify timezone setting:** Settings → Timezone
3. **Check schedule entries:** Schedule Editor → verify date matches today
4. **View scheduler jobs:** Diagnostics → Scheduler Jobs section
5. **Reload config:** Scheduler → Reload All Schedules

### Audio File Not Found

1. **Use File Management → Verify Files**
2. **Check file paths in schedule.xlsx match actual files**
3. **Ensure files are in /data directory**
4. **Verify file extensions match supported formats**

### Dashboard Can't Connect to Bot API

1. **Check bot container is running:**
   ```bash
   docker ps
   ```

2. **Check API health:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Restart containers:**
   ```bash
   docker-compose restart
   ```

### Audio Conversion Fails

1. **Check FFmpeg is installed:**
   ```bash
   docker exec telegram-audio-bot ffmpeg -version
   ```

2. **Verify audio file is valid**
3. **Check disk space for cache directory**
4. **Review logs for FFmpeg errors**

## Development

### Running Locally (Without Docker)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export PYTHONUNBUFFERED=1
export BOT_LOG_LEVEL=INFO
export BOT_API_URL=http://localhost:8000
export DATA_DIR=./data
```

3. **Run bot (Terminal 1):**
```bash
python -m bot.main
```

4. **Run dashboard (Terminal 2):**
```bash
streamlit run dashboard/app.py
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_audio_converter.py -v
```

### Code Structure

- **bot/**: Bot container code
  - `main.py`: Application entry point
  - `config.py`: Configuration management
  - `scheduler.py`: APScheduler integration
  - `telegram_handler.py`: Telegram bot management
  - `api_server.py`: FastAPI server
  - `utils/`: Audio converter, file validator, Excel parser

- **dashboard/**: Dashboard container code
  - `app.py`: Streamlit entry point
  - `pages/`: 7 dashboard pages
  - `components/`: Reusable UI components
  - `api_client.py`: HTTP client for bot API

- **shared/**: Shared between containers
  - `models.py`: Pydantic models
  - `constants.py`: Application constants
  - `database.py`: JSON database utilities

## Logging

All logs are written to `/data/logs/` with automatic rotation:

- **bot.log**: Main bot activity, sends, errors
- **scheduler.log**: Scheduler events, job execution
- **Max file size**: 10MB
- **Backup count**: 5 files

View logs via:
- Dashboard → Diagnostics → Recent Logs
- Docker: `docker logs telegram-audio-bot`
- Direct: `tail -f data/logs/bot.log`

## Performance Considerations

- Audio files are converted once and cached in `/data/.audio_cache/`
- Excel schedule parsed on-demand (not kept in memory)
- FastAPI uses async/await throughout for non-blocking I/O
- APScheduler uses asyncio for efficient scheduling
- Streamlit auto-caches page components

## Security Notes

- **Bot tokens** stored in `config.json` - protect this file
- **Chat IDs** visible in dashboard - restrict dashboard access
- **API endpoints** should be firewalled in production
- **Docker network** provides isolation between containers
- Consider using **secrets manager** for production deployments

## Production Deployment

### Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart specific container
docker-compose restart bot
docker-compose restart dashboard
```

### Environment-Specific Configuration

Create `.env` file:
```env
TZ=America/New_York
BOT_LOG_LEVEL=WARNING
```

### Backup Strategy

```bash
# Backup data directory
tar -czf telegram-bot-backup-$(date +%Y%m%d).tar.gz data/

# Restore
tar -xzf telegram-bot-backup-YYYYMMDD.tar.gz
```

### Monitoring

- Enable auto-refresh in Diagnostics page
- Set up external monitoring for API health endpoint
- Monitor disk usage for audio cache
- Set up log aggregation (e.g., ELK stack)

## Maintenance

### Update Application

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Clean Audio Cache

```bash
# Remove cached OGG files
rm -rf data/.audio_cache/*
```

### Rotate Logs Manually

```bash
# Keep last 100 lines of each log
cd data/logs
for log in *.log; do tail -100 "$log" > "$log.tmp" && mv "$log.tmp" "$log"; done
```

### Database Maintenance

Config and state are stored in JSON files:
- `config.json`: Bot configurations (backed up automatically)
- `bot_state.json`: Runtime state (can be deleted safely)

## FAQ

**Q: Can I use this with multiple Telegram accounts?**
A: Yes! Add multiple bots in Configuration tab. Each bot can have its own token, chat ID, and schedule time.

**Q: What audio formats are supported?**
A: MP3, OGG, WAV, M4A. All formats are converted to OGG OPUS for Telegram.

**Q: How do I get my Chat ID?**
A: Use [@userinfobot](https://t.me/userinfobot) or [@getidsbot](https://t.me/getidsbot) on Telegram.

**Q: Can I send to groups/channels?**
A: Yes! Add your bot to the group/channel and use the group/channel ID as chat_id.

**Q: What if my schedule.xlsx gets corrupted?**
A: Use Schedule Editor → Create Template to start fresh.

**Q: How do I change the schedule without restarting?**
A: Edit schedule.xlsx in Schedule Editor. Changes take effect at next scheduled run.

**Q: Can I test sends before the scheduled time?**
A: Yes! Use Manual Send tab to test individual files or entire dates.

**Q: What happens if a file is missing?**
A: The bot logs an error and continues with remaining files. Check Diagnostics for errors.

## Technology Stack

- **Language**: Python 3.9+
- **Bot Framework**: python-telegram-bot 20.5 (async)
- **Audio Processing**: FFmpeg, pydub
- **Scheduling**: APScheduler 3.10 with timezone support
- **API**: FastAPI 0.104
- **Dashboard**: Streamlit 1.28
- **Excel**: openpyxl 3.1
- **Data Validation**: Pydantic 2.4
- **HTTP Client**: httpx (async)
- **Containerization**: Docker + Docker Compose

## License

Production Ready - Internal Use

## Support

For issues:
1. Check Diagnostics → Logs
2. Review this README
3. Check Docker logs: `docker logs telegram-audio-bot`

## Version

**Current Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2024

---

**Made with ❤️ for automated Telegram broadcasting**
