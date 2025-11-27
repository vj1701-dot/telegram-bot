# Deployment Checklist

## Pre-Deployment

### 1. Prerequisites
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Telegram Bot Token obtained from @BotFather
- [ ] Chat ID obtained (use @userinfobot)
- [ ] Audio files prepared (MP3, OGG, WAV, or M4A)

### 2. Environment Setup
- [ ] Navigate to project directory
- [ ] Review `docker-compose.yml`
- [ ] Review `.env.example` (optional customization)
- [ ] Ensure ports 8000 and 8501 are available

## Deployment Steps

### 3. Build & Start
```bash
# Build containers
docker-compose build

# Start in detached mode
docker-compose up -d

# Verify containers are running
docker ps
```

Expected output: 2 containers running
- `telegram-audio-bot`
- `streamlit-dashboard`

### 4. Health Checks
- [ ] Wait 30 seconds for initialization
- [ ] Access dashboard: http://localhost:8501
- [ ] Check sidebar shows "✓ Bot API Connected"
- [ ] Check API health: http://localhost:8000/health

### 5. Initial Configuration

#### A. Add Bot
- [ ] Go to Configuration → Add Bot
- [ ] Enter Bot Token
- [ ] Enter Chat ID
- [ ] Set scheduler time (e.g., 09:00)
- [ ] Click "Test" to verify connection
- [ ] Click "Add Bot"

#### B. Set Timezone
- [ ] Go to Settings → Timezone
- [ ] Select your timezone
- [ ] Click "Update Timezone"

#### C. Create Schedule
- [ ] Go to Schedule Editor
- [ ] Click "Create Template Schedule" (or upload existing)
- [ ] Edit dates to match your needs
- [ ] Save schedule

#### D. Upload Audio
- [ ] Go to File Management → Upload Files
- [ ] Select or create target folder
- [ ] Upload audio files
- [ ] Click "Upload Files"

### 6. Verification

#### A. File Verification
- [ ] Go to File Management → Verify Files
- [ ] Click "Verify All Files"
- [ ] Confirm all files show ✓ (green checkmarks)
- [ ] Fix any missing files

#### B. Manual Test Send
- [ ] Go to Manual Send
- [ ] Select your bot
- [ ] Select a test audio file
- [ ] Click "Send Now"
- [ ] Check Telegram to confirm receipt
- [ ] Verify audio plays correctly

#### C. Scheduler Verification
- [ ] Go to Scheduler
- [ ] Verify schedule time is correct
- [ ] Check timezone is correct
- [ ] Note the "Next Run" time
- [ ] Confirm it matches expectations

### 7. Monitoring Setup

#### A. Check Diagnostics
- [ ] Go to Diagnostics
- [ ] Verify "Bot API is Online"
- [ ] Check bot status shows "Healthy"
- [ ] Review recent logs
- [ ] No errors visible

#### B. Enable Auto-Refresh
- [ ] In Diagnostics, enable "Auto-refresh (5s)"
- [ ] Watch for updates
- [ ] Disable when satisfied

## Post-Deployment

### 8. Production Readiness

#### A. Documentation
- [ ] Review README.md
- [ ] Bookmark QUICKSTART.md
- [ ] Note API docs: http://localhost:8000/docs

#### B. Backup Strategy
```bash
# Backup data directory
tar -czf telegram-bot-backup-$(date +%Y%m%d).tar.gz data/

# Store backup securely
```

#### C. Monitoring Plan
- [ ] Schedule regular diagnostics checks
- [ ] Set up log review process
- [ ] Monitor disk space in /data
- [ ] Plan for log rotation

### 9. Operational Procedures

#### A. Daily Checks
- [ ] Review Diagnostics → Bot Status
- [ ] Check for errors in logs
- [ ] Verify scheduled sends occurred

#### B. Weekly Maintenance
- [ ] Review and clean logs
- [ ] Check audio cache size
- [ ] Verify schedule is up-to-date
- [ ] Backup config.json

#### C. Monthly Tasks
- [ ] Review all bot configurations
- [ ] Update audio files as needed
- [ ] Check for application updates
- [ ] Test disaster recovery

## Troubleshooting Commands

```bash
# View bot logs
docker logs telegram-audio-bot

# View dashboard logs
docker logs streamlit-dashboard

# Restart specific container
docker-compose restart bot
docker-compose restart dashboard

# Restart all
docker-compose restart

# Stop all
docker-compose down

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Enter bot container
docker exec -it telegram-audio-bot bash

# Check FFmpeg
docker exec telegram-audio-bot ffmpeg -version
```

## Common Issues & Solutions

### Issue: Bot API Offline
**Solution:**
```bash
docker logs telegram-audio-bot
docker-compose restart bot
```

### Issue: Files Not Found
**Solution:**
- Check File Management → Verify Files
- Ensure paths in schedule.xlsx match actual files
- Verify file extensions are correct

### Issue: Schedule Not Running
**Solution:**
- Check Scheduler → verify time is correct
- Verify timezone in Settings
- Reload config: Scheduler → Reload All Schedules

### Issue: Can't Access Dashboard
**Solution:**
- Check if port 8501 is available
- Verify container is running: `docker ps`
- Check dashboard logs: `docker logs streamlit-dashboard`

## Rollback Procedure

If deployment fails:

```bash
# Stop containers
docker-compose down

# Restore backup
tar -xzf telegram-bot-backup-YYYYMMDD.tar.gz

# Restart
docker-compose up -d
```

## Success Criteria

Deployment is successful when:
- ✅ Both containers running
- ✅ Dashboard accessible at http://localhost:8501
- ✅ API healthy at http://localhost:8000/health
- ✅ Bot connection test passes
- ✅ Manual send test works
- ✅ All schedule files verify successfully
- ✅ No errors in logs
- ✅ Scheduler shows correct next run time

## Production Checklist

Before going to production:
- [ ] All tests completed
- [ ] Bot credentials verified
- [ ] Schedule finalized
- [ ] Audio files uploaded and verified
- [ ] Timezone configured correctly
- [ ] Manual send test successful
- [ ] Backup created
- [ ] Monitoring enabled
- [ ] Documentation reviewed
- [ ] Team trained on dashboard

## Security Checklist

- [ ] config.json protected (appropriate file permissions)
- [ ] API not exposed to internet (firewall configured)
- [ ] Docker network isolated
- [ ] No credentials in logs
- [ ] Regular backups scheduled
- [ ] Access to dashboard restricted

## Scaling Considerations

For high-volume deployments:
- [ ] Monitor CPU usage
- [ ] Monitor memory usage
- [ ] Monitor disk space
- [ ] Consider log aggregation
- [ ] Plan for audio cache growth
- [ ] Consider rate limiting

## Maintenance Schedule

| Frequency | Task | Responsible |
|-----------|------|-------------|
| Daily | Check diagnostics | Operator |
| Daily | Verify sends occurred | Operator |
| Weekly | Review logs | Admin |
| Weekly | Backup data | Admin |
| Monthly | Update schedule | Content team |
| Monthly | Clean audio cache | Admin |
| Quarterly | Review all configs | Admin |

## Contact & Support

- Technical Documentation: README.md
- Quick Start: QUICKSTART.md
- API Documentation: http://localhost:8000/docs
- Logs: Dashboard → Diagnostics
- Docker Logs: `docker logs telegram-audio-bot`

---

**Deployment Date**: ___________
**Deployed By**: ___________
**Version**: 1.0.0
**Status**: ⬜ Pre-deployment ⬜ Deployed ⬜ Production
