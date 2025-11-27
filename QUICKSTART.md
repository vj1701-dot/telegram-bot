# Quick Start Guide

## 1. Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy your bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 2. Get Your Chat ID

**For personal messages:**
1. Send a message to [@userinfobot](https://t.me/userinfobot)
2. Copy your ID

**For channels/groups:**
1. Add your bot to the channel/group
2. Make it admin if needed
3. Use [@getidsbot](https://t.me/getidsbot) to get the chat ID

## 3. Start the Application

```bash
# In the project directory
docker-compose up -d --build
```

Wait ~30 seconds for containers to start.

## 4. Access Dashboard

Open browser: http://localhost:8501

## 5. Configure Your Bot

1. Click **Configuration** in sidebar
2. Click **Add Bot** tab
3. Enter:
   - Bot Token: (from step 1)
   - Chat ID: (from step 2)
   - Schedule Time: 09:00 (or preferred time)
4. Click **Test** to verify connection
5. Click **Add Bot**

## 6. Create Schedule

1. Click **Schedule Editor**
2. Click **Create Template Schedule**
3. Edit the schedule:
   - Date: YYYY-MM-DD format
   - Path: `audio/` (or subfolder)
   - Track Name: your MP3 filename
   - Enabled: TRUE
4. Click **Save Schedule**

## 7. Upload Audio Files

1. Click **File Management**
2. Select **Upload Files** tab
3. Choose target folder: `audio/`
4. Upload your MP3/OGG/WAV files
5. Click **Upload Files**

## 8. Verify Setup

1. Click **File Management** → **Verify Files** tab
2. Click **Verify All Files**
3. Ensure all files show ✓ (green checkmarks)

## 9. Test Manual Send

1. Click **Manual Send**
2. Select your bot
3. Choose "Browse Files" or enter path manually
4. Click **Send Now**
5. Check your Telegram to confirm receipt

## 10. Monitor

1. Click **Diagnostics**
2. Check "Bot Status" section
3. View logs if needed
4. Enable auto-refresh for real-time monitoring

## Next Steps

- **Set Timezone**: Settings → Timezone → Select your timezone
- **Adjust Schedule Time**: Scheduler → Update schedule times
- **Add More Bots**: Configuration → Add Bot (repeat for multiple bots)
- **View Logs**: Diagnostics → Recent Logs

## Troubleshooting

**Bot won't send:**
- Check bot token and chat ID in Configuration
- Verify bot is added to channel/group (if using one)
- Test connection in Configuration tab

**Files not found:**
- Use File Management → Verify Files
- Ensure filenames in schedule.xlsx match uploaded files exactly
- Check file paths start with `audio/`

**Need help?**
- Check full README.md
- Review logs in Diagnostics
- Run: `docker logs telegram-audio-bot`

## Example Schedule

| Date       | Path      | Track Name       | Enabled |
|------------|-----------|------------------|---------|
| 2024-01-15 | audio/    | morning.mp3      | TRUE    |
| 2024-01-15 | audio/    | news.mp3         | TRUE    |
| 2024-01-16 | audio/    | daily_brief.mp3  | TRUE    |

File structure:
```
data/
└── audio/
    ├── morning.mp3
    ├── news.mp3
    └── daily_brief.mp3
```

That's it! Your Telegram Audio Bot is ready to go! 🎉
