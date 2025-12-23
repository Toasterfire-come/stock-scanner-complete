# Windows Task Scheduler Setup Guide

## Overview
This guide helps you set up automated scanning using **Windows Task Scheduler** (the Windows equivalent of cron jobs).

## ⚠️ Important Note
Windows does **NOT** have `crontab`. Instead, we use **Windows Task Scheduler** to run scripts on a schedule.

## Quick Installation

### Step 1: Run the Installation Script

Open Command Prompt **as Administrator** and run:

```cmd
cd C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend
install_windows_scheduled_tasks.bat
```

This will automatically create all necessary scheduled tasks.

### Step 2: Verify Installation

Check that tasks were created:

```cmd
schtasks /Query /TN "TradeScanPro\*"
```

## Scheduled Tasks Created

The installation script creates the following tasks:

### 1. **Refresh Proxies** - Daily at 1:00 AM
- **Task Name**: `TradeScanPro\RefreshProxies`
- **Script**: `refresh_proxies.bat`
- **Frequency**: Every day at 1:00 AM
- **Purpose**: Fetch fresh proxies from Geonode API

### 2. **Daily Scanner** - Daily at 2:00 AM
- **Task Name**: `TradeScanPro\DailyScanner`
- **Script**: `realtime_daily_yfinance.py`
- **Frequency**: Every day at 2:00 AM
- **Purpose**: Comprehensive daily scan of all stocks

### 3. **10-Minute Scanner** - Weekdays during market hours
- **Task Name**: `TradeScanPro\10MinScanner`
- **Script**: `scanner_10min_metrics_improved.py`
- **Frequency**: Every 10 minutes from 9:30 AM to 4:00 PM (Mon-Fri)
- **Purpose**: Update volume and metrics during trading hours

### 4. **1-Minute Scanner Start** - Weekdays at 9:25 AM
- **Task Name**: `TradeScanPro\1MinScanner_Start`
- **Script**: `scanner_1min_hybrid.py`
- **Frequency**: Monday-Friday at 9:25 AM
- **Purpose**: Start real-time WebSocket price scanner

### 5. **1-Minute Scanner Stop** - Weekdays at 4:05 PM
- **Task Name**: `TradeScanPro\1MinScanner_Stop`
- **Frequency**: Monday-Friday at 4:05 PM
- **Purpose**: Stop the 1-minute scanner after market close

## Manual Task Management

### View All Tasks
```cmd
schtasks /Query /TN "TradeScanPro\*"
```

### View Task Details
```cmd
schtasks /Query /TN "TradeScanPro\DailyScanner" /V /FO LIST
```

### Run a Task Immediately (for testing)
```cmd
schtasks /Run /TN "TradeScanPro\DailyScanner"
```

### Disable a Task
```cmd
schtasks /Change /TN "TradeScanPro\DailyScanner" /DISABLE
```

### Enable a Task
```cmd
schtasks /Change /TN "TradeScanPro\DailyScanner" /ENABLE
```

### Delete a Specific Task
```cmd
schtasks /Delete /TN "TradeScanPro\DailyScanner" /F
```

### Delete All TradeScanPro Tasks
```cmd
schtasks /Delete /TN "TradeScanPro\*" /F
```

### Open Task Scheduler GUI
```cmd
taskschd.msc
```

In the GUI, navigate to **Task Scheduler Library → TradeScanPro** to see all tasks.

## Log Files

All logs are written to `backend\logs\`:

- `proxy_refresh.log` - Proxy refresh operations
- `daily_scanner.log` - Daily comprehensive scans
- `10min_scanner.log` - 10-minute metrics scans
- `1min_scanner.log` - 1-minute price updates

### View Logs in Real-Time

**PowerShell:**
```powershell
Get-Content backend\logs\daily_scanner.log -Wait -Tail 50
```

**Command Prompt:**
```cmd
type backend\logs\daily_scanner.log
```

**Git Bash:**
```bash
tail -f backend/logs/daily_scanner.log
```

## Manual Script Execution (Testing)

You can run any scanner manually to test:

### Daily Scanner
```cmd
cd C:\Stock-scanner-project\v2mvp-stock-scanner-complete\stock-scanner-complete\backend
python realtime_daily_yfinance.py
```

### 10-Minute Scanner
```cmd
python scanner_10min_metrics_improved.py
```

### 1-Minute Scanner
```cmd
python scanner_1min_hybrid.py
```

### Proxy Refresh
```cmd
refresh_proxies.bat
```

## Troubleshooting

### Tasks Not Running?

1. **Check Task Scheduler Service**
   ```cmd
   sc query "Task Scheduler"
   ```
   Should show `STATE: RUNNING`. If not:
   ```cmd
   net start "Task Scheduler"
   ```

2. **Verify Tasks Exist**
   ```cmd
   schtasks /Query /TN "TradeScanPro\*"
   ```

3. **Check Task History**
   - Open Task Scheduler GUI: `taskschd.msc`
   - Navigate to TradeScanPro folder
   - Right-click task → Properties → History tab

4. **Check Logs for Errors**
   ```cmd
   type backend\logs\daily_scanner.log
   ```

5. **Test Script Manually**
   Run the script directly to see if there are any errors:
   ```cmd
   python realtime_daily_yfinance.py
   ```

### Python Not Found?

If tasks fail because Python isn't found:

1. **Find Python Path**
   ```cmd
   where python
   ```

2. **Edit the installation script** and hardcode the Python path:
   - Open `install_windows_scheduled_tasks.bat`
   - Change `%PYTHON_BIN%` to your full Python path (e.g., `C:\Python39\python.exe`)

### Permission Issues?

Run Command Prompt **as Administrator** when:
- Installing tasks
- Running tasks manually
- Deleting tasks

## Differences from Linux Cron

| Feature | Linux Cron | Windows Task Scheduler |
|---------|------------|------------------------|
| Command | `crontab -e` | `schtasks` or GUI |
| List jobs | `crontab -l` | `schtasks /Query` |
| Remove jobs | `crontab -r` | `schtasks /Delete` |
| Run as | Current user | Specified user |
| GUI | No | Yes (`taskschd.msc`) |

## Dependencies

### Required Software
- **Python 3.x** - Must be in PATH
- **curl** - Built into Windows 10+ (for proxy refresh)
- **PowerShell** - Built into Windows (for JSON parsing)

### Optional
- **Git Bash** - For Unix-like commands and running `.sh` scripts

## Security Notes

- Tasks run with the permissions of the user who created them
- For production, consider running as a dedicated service account
- Ensure log directory has proper write permissions
- Review scheduled tasks regularly for security

## Advanced Configuration

### Change Schedule Times

Edit times in `install_windows_scheduled_tasks.bat`:
- `/ST 02:00` - Start time (2:00 AM)
- `/RI 10` - Repeat interval (10 minutes)
- `/DU 06:30` - Duration (6 hours 30 minutes)

Then re-run the installation script.

### Run on Specific Days

Current setup runs weekday tasks on Monday-Friday:
```cmd
/D MON,TUE,WED,THU,FRI
```

To change, edit the installation script and modify the `/D` parameter.

## Production Recommendations

1. **Test First**: Run all scripts manually before scheduling
2. **Monitor Logs**: Check logs daily for the first week
3. **Set Alerts**: Use Windows Event Viewer to alert on task failures
4. **Backup Database**: Schedule regular database backups
5. **Resource Monitoring**: Monitor CPU/memory usage during scans
6. **Network Monitoring**: Watch for rate limiting or IP bans

## Support

For issues:
1. Check log files first
2. Verify Python environment
3. Test scripts manually
4. Review Task Scheduler event history
5. Check Windows Event Viewer for system errors
