# Telegram Audio Bot - Simplified Setup

A simple, single-container Telegram audio bot with a clean HTML web interface.

## What Changed?

- ✅ Removed Streamlit (too complex, too many bugs)
- ✅ Single Docker container instead of two
- ✅ Simple HTML UI served by FastAPI
- ✅ No bot polling (send-only, one-way communication)
- ✅ Much smaller, faster, simpler

## Quick Start

1. **Build and start:**
```bash
docker-compose up -d --build
```

2. **Access the web UI:**
- Open: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Using the Web UI

### 1. Configure Bot
- Go to "Configuration" tab
- Enter your Bot Token (from @BotFather)
- Enter Chat ID (your channel/group ID)
- Set daily send time
- Click "Add Bot"

### 2. Upload Audio Files
- Go to "Upload Files" tab
- Select multiple audio files (MP3, OGG, WAV, M4A)
- Choose target folder
- Upload

### 3. Create Schedule
- Create an Excel file with columns:
  - **Date**: YYYY-MM-DD format
  - **Path**: audio/ or audio/subfolder/
  - **Track Name**: filename.mp3
  - **Enabled**: TRUE or FALSE
- Upload via "Schedule" tab

### 4. Manual Send
- Go to "Manual Send" tab
- Enter date (YYYY-MM-DD)
- Bot will send all audio for that date

## File Structure

```
telegram-audio-bot/
├── bot/                  # Bot code
│   ├── main.py          # Entry point
│   ├── api_server.py    # FastAPI + HTML UI
│   ├── telegram_handler.py
│   ├── scheduler.py
│   └── web/
│       └── templates/
│           └── index.html  # Simple HTML UI
├── data/                # Your files (mounted volume)
│   ├── config.json      # Bot configuration
│   ├── schedule.xlsx    # Schedule file
│   └── audio/           # Audio files
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## How It Works

1. **Scheduler**: Runs daily at configured time, sends audio based on schedule.xlsx
2. **Web UI**: Simple HTML interface for configuration and manual operations
3. **API**: FastAPI endpoints for all operations (see /docs)
4. **One-way**: Bot only sends messages, doesn't listen for commands

## Troubleshooting

**Container won't start?**
```bash
docker-compose logs
```

**Can't access UI?**
- Make sure port 8000 is available
- Check: http://localhost:8000/health

**Audio not sending?**
- Check schedule.xlsx format
- Verify audio files exist in /data/audio/
- Check logs: `docker-compose logs`

## Manual Operations (via API)

You can also use the API directly:

```bash
# Send audio for specific date
curl -X POST http://localhost:8000/api/send-manual \
  -F "date=2024-01-15"

# Upload file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@audio.mp3" \
  -F "folder=audio/"

# Get status
curl http://localhost:8000/api/status
```

## Advantages of New Setup

- **Faster**: Single container, no Streamlit overhead
- **Simpler**: Just HTML + FastAPI, no complex dependencies
- **Smaller**: ~50% fewer packages
- **Cleaner**: No mysterious Streamlit errors
- **Direct**: Everything in one place, one port

Enjoy your simplified bot! 🎙️
