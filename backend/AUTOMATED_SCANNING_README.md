# Automated Scanning Setup

## Choose Your Platform

This repository includes scripts for both **Linux/Unix** and **Windows** platforms.

---

## 🪟 Windows Users (RECOMMENDED)

**You are running Windows**, so use the **Windows Task Scheduler** setup:

### Quick Start
```cmd
cd C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend
install_windows_scheduled_tasks.bat
```

### Full Documentation
See **[WINDOWS_SCHEDULER_SETUP.md](WINDOWS_SCHEDULER_SETUP.md)** for complete instructions.

---

## 🐧 Linux/Unix Users

If you're deploying to a Linux server, use the **cron** setup:

### Quick Start
```bash
cd /path/to/backend
./install_cron_jobs.sh
```

### Full Documentation
See **[CRON_JOBS_SETUP.md](CRON_JOBS_SETUP.md)** for complete instructions.

---

## 📋 What Gets Scheduled

Both platforms set up the same scanning schedule:

| Time | Task | Description |
|------|------|-------------|
| **1:00 AM** | Proxy Refresh | Fetch fresh proxies from Geonode API |
| **2:00 AM** | Daily Scanner | Comprehensive scan of all stocks |
| **9:25 AM** (Mon-Fri) | Start 1-Min Scanner | Begin real-time WebSocket price updates |
| **9:30 AM - 4:00 PM** (Mon-Fri) | 10-Min Scanner | Update metrics every 10 minutes |
| **4:05 PM** (Mon-Fri) | Stop 1-Min Scanner | Stop real-time scanner after market close |

---

## 📁 Files Included

### Windows Files
- `install_windows_scheduled_tasks.bat` - Windows installer
- `refresh_proxies.bat` - Windows proxy refresh script
- `WINDOWS_SCHEDULER_SETUP.md` - Windows documentation

### Linux/Unix Files
- `install_cron_jobs.sh` - Linux installer
- `refresh_proxies.sh` - Linux proxy refresh script
- `CRON_JOBS_SETUP.md` - Linux documentation

### Python Scanners (Cross-Platform)
- `realtime_daily_yfinance.py` - Daily comprehensive scanner
- `scanner_10min_metrics_improved.py` - 10-minute metrics scanner
- `scanner_1min_hybrid.py` - 1-minute WebSocket price scanner

---

## 🚀 Quick Setup (Windows)

Since you're on Windows, here's the fastest way to get started:

1. **Open Command Prompt as Administrator**
   - Press `Win + X`
   - Select "Command Prompt (Admin)" or "PowerShell (Admin)"

2. **Navigate to backend directory**
   ```cmd
   cd C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend
   ```

3. **Run the installer**
   ```cmd
   install_windows_scheduled_tasks.bat
   ```

4. **Verify installation**
   ```cmd
   schtasks /Query /TN "TradeScanPro\*"
   ```

That's it! Your scanners are now scheduled.

---

## 📊 Monitor Your Scanners

### View Logs
All logs are in `backend\logs\`:

```cmd
REM View daily scanner log
type logs\daily_scanner.log

REM View 10-minute scanner log
type logs\10min_scanner.log

REM Watch logs in real-time (PowerShell)
Get-Content logs\daily_scanner.log -Wait -Tail 50
```

### Check Scheduled Tasks
```cmd
REM List all tasks
schtasks /Query /TN "TradeScanPro\*"

REM Open Task Scheduler GUI
taskschd.msc
```

### Run Tasks Manually (Testing)
```cmd
REM Test daily scanner
schtasks /Run /TN "TradeScanPro\DailyScanner"

REM Or run Python directly
python realtime_daily_yfinance.py
```

---

## 🔧 Troubleshooting

### Common Issues

**1. "crontab: command not found"**
- You're on Windows! Use `install_windows_scheduled_tasks.bat` instead.

**2. Tasks not running?**
- Ensure Task Scheduler service is running: `sc query "Task Scheduler"`
- Check you ran the installer as Administrator
- View logs: `type logs\daily_scanner.log`

**3. Python not found?**
- Verify Python is in PATH: `where python`
- Or edit the installer to use full Python path

**4. Permission denied?**
- Run Command Prompt as Administrator
- Check log directory permissions

---

## 📚 Documentation

- **Windows Setup**: [WINDOWS_SCHEDULER_SETUP.md](WINDOWS_SCHEDULER_SETUP.md)
- **Linux Setup**: [CRON_JOBS_SETUP.md](CRON_JOBS_SETUP.md)
- **Scanner Usage**: [SCRIPT_USAGE_GUIDE.md](SCRIPT_USAGE_GUIDE.md) (if exists)

---

## 🎯 Next Steps

1. **Install the scheduler** (see Quick Setup above)
2. **Test manually** - Run one scanner to ensure it works
3. **Check logs** - Verify output is being logged correctly
4. **Monitor for a week** - Watch logs to ensure scheduled runs are working
5. **Adjust schedule** - Modify times if needed for your timezone

---

## 💡 Tips

- **Always test manually first** before relying on scheduled tasks
- **Check logs daily** for the first week to catch any issues
- **Keep proxy list fresh** - The daily proxy refresh helps avoid rate limits
- **Monitor database size** - Ensure adequate disk space for logs and data
- **Set up alerts** - Use Windows Event Viewer to alert on task failures

---

## ⚠️ Important Notes

- **Windows vs Linux**: This repo supports both, but use Windows tools on Windows
- **Time zones**: All times are in your local system time
- **Market hours**: Adjust 9:30 AM - 4:00 PM if you're in a different timezone than US Eastern
- **Proxies**: Free proxies have limited reliability; consider paid proxies for production

---

**Need Help?**

Check the platform-specific documentation:
- Windows: [WINDOWS_SCHEDULER_SETUP.md](WINDOWS_SCHEDULER_SETUP.md)
- Linux: [CRON_JOBS_SETUP.md](CRON_JOBS_SETUP.md)
