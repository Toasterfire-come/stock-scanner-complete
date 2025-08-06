# Stock Scanner Scheduler - Windows/Hosted Environment Setup

## 🚀 **Quick Setup for WordPress Hosted on IONOS with Cloudflare Tunnel**

This guide is specifically designed for Windows users managing a WordPress installation hosted on IONOS, with a Django API accessible via Cloudflare tunnel.

### ✅ **Prerequisites**

1. **PHP 7.4 or higher** installed on your Windows machine
   - Download from: https://www.php.net/downloads
   - Add PHP to your Windows PATH environment variable

2. **WordPress hosted on IONOS** (or similar hosting provider)
   - Active WordPress installation
   - Access to WordPress admin panel
   - FTP/File Manager access to upload plugins

3. **Cloudflare Tunnel** set up for your Django API
   - Your tunnel URL (e.g., `https://your-tunnel.trycloudflare.com`)
   - API accessible at `https://your-tunnel.trycloudflare.com/api/`

4. **Windows Bash/Command Line** access

### 📁 **Installation Steps**

#### Step 1: Upload Plugin to WordPress

1. **Upload Plugin Files:**
   ```
   wordpress_plugin/stock-scanner-integration/
   ├── stock-scanner-integration.php
   ├── includes/
   │   ├── class-scheduler.php
   │   ├── class-admin-dashboard.php
   │   └── ... (other files)
   ├── assets/
   │   ├── css/
   │   ├── js/
   │   └── ...
   └── templates/
   ```

2. **Upload via FTP or WordPress File Manager:**
   - Navigate to `/wp-content/plugins/`
   - Upload the entire `stock-scanner-integration` folder

3. **Activate Plugin:**
   - Go to WordPress Admin → Plugins
   - Find "Stock Scanner Professional"
   - Click "Activate"

#### Step 2: Download Management Scripts

1. **Download to your Windows machine:**
   - `manage_scheduler_windows.php`
   - `scheduler.bat`

2. **Place in a working directory on your Windows machine**
   (e.g., `C:\stock-scanner\`)

#### Step 3: Configure API Connection

1. **Run the configuration tool:**
   ```bash
   # Option 1: Using batch file (interactive)
   scheduler.bat

   # Option 2: Using PHP directly
   php manage_scheduler_windows.php config
   ```

2. **Enter your Cloudflare tunnel URL:**
   ```
   Example: https://your-tunnel.trycloudflare.com
   ```

3. **Test the connection:**
   ```bash
   php manage_scheduler_windows.php test
   ```

### 🎯 **Usage**

#### Easy Method: Interactive Batch File

1. **Double-click `scheduler.bat`** or run from command line
2. **Choose from the menu:**
   ```
   1. Start Scheduler     - Begin automatic data collection
   2. Stop Scheduler      - Stop all scheduled tasks
   3. Restart Scheduler   - Restart the system
   4. Check Status        - View current status
   5. Test API Connection - Test Cloudflare tunnel
   6. View Logs          - See recent activity
   7. System Check       - Comprehensive diagnostics
   8. Market Status      - Current market hours
   9. Configure API      - Set/change API URL
   ```

#### Command Line Method

```bash
# Start the scheduler
php manage_scheduler_windows.php start

# Check status
php manage_scheduler_windows.php status

# Stop the scheduler
php manage_scheduler_windows.php stop

# View market status
php manage_scheduler_windows.php market

# Run system diagnostics
php manage_scheduler_windows.php syscheck
```

### ⚙️ **How It Works**

#### WordPress Cron-Based System

Unlike traditional server-based schedulers, this system uses **WordPress cron** for hosted environments:

1. **Market Hours Detection:**
   - Automatically starts data collection at 4:00 AM ET (pre-market)
   - Stops data collection at 8:00 PM ET (post-market)
   - Pauses on weekends

2. **3-Minute Intelligent Intervals:**
   - Stock updates every 3 minutes
   - News updates every 3 minutes (offset by 90 seconds)
   - Smart delay calculation: `180 seconds - execution_time`

3. **WordPress Cron Jobs:**
   - `stock_scanner_update_stocks` - Stock data collection
   - `stock_scanner_update_news` - News data collection  
   - `stock_scanner_market_check` - Market hours monitoring
   - `stock_scanner_system_check` - Health monitoring

4. **API Communication:**
   - Calls your Django API via Cloudflare tunnel
   - Endpoints: `/api/stocks/update/`, `/api/news/update/`, `/api/health/`

### 🔧 **Configuration**

#### WordPress Settings

The plugin automatically configures itself, but you can verify:

1. **WordPress Admin → Stock Scanner:**
   - Dashboard should show market status
   - Settings page allows API URL configuration

2. **WordPress Cron Status:**
   - Ensure `DISABLE_WP_CRON` is NOT set to `true` in `wp-config.php`
   - Most hosting providers (including IONOS) support WordPress cron

#### API Endpoints Required

Your Django API should respond to:

```
GET  /api/health/              - Health check
POST /api/stocks/update/       - Trigger stock data update
POST /api/news/update/         - Trigger news data update
```

Example expected response:
```json
{
    "status": "success",
    "message": "Data updated successfully"
}
```

### 📊 **Monitoring**

#### Status Display

```bash
php manage_scheduler_windows.php status
```

Shows:
- ✅ **Scheduler Status:** Active/Inactive
- 🏛️ **Market Status:** Open/Closed with session info
- 📊 **Data Collection:** Active/Paused
- ⏰ **Next Scheduled Jobs:** Countdown timers
- 🌐 **API Configuration:** Current tunnel URL

#### Market Hours Awareness

```bash
php manage_scheduler_windows.php market
```

Displays:
- Current Eastern Time
- Market session (Pre-market/Regular/Post-market/Closed)
- Next market open time
- Data collection status

### 🚨 **Troubleshooting**

#### Common Issues

1. **"WordPress cron is disabled"**
   - Edit `wp-config.php`
   - Remove or comment out: `define('DISABLE_WP_CRON', true);`

2. **"API not reachable"**
   - Check Cloudflare tunnel is running
   - Verify URL format: `https://your-tunnel.trycloudflare.com`
   - Test manually: `curl https://your-tunnel.trycloudflare.com/api/health/`

3. **"Plugin not active"**
   - WordPress Admin → Plugins → Activate "Stock Scanner Professional"
   - Check file permissions in `/wp-content/plugins/`

4. **"No WordPress cron jobs scheduled"**
   - Run: `php manage_scheduler_windows.php start`
   - Check WordPress Admin → Tools → Cron Events (if plugin available)

#### System Check

```bash
php manage_scheduler_windows.php syscheck
```

Checks:
- ✅ API connectivity via Cloudflare tunnel
- ✅ WordPress database connection
- ✅ Plugin activation status
- ✅ WordPress cron availability
- ✅ File permissions
- ✅ Current market status

### 🕐 **Automatic Operation**

Once started, the system:

1. **Monitors market hours every 5 minutes**
2. **Starts data collection at 4:00 AM ET**
3. **Collects stock data every 3 minutes during market hours**
4. **Collects news data every 3 minutes (offset)**
5. **Stops data collection at 8:00 PM ET**
6. **Pauses on weekends**
7. **Resumes Monday at 4:00 AM ET**

### 📝 **WordPress Integration**

#### Frontend Display

The plugin creates these WordPress pages automatically:
- `/stock-scanner-dashboard/` - Main dashboard
- `/premium-plans/` - Membership plans
- `/stock-scanner/` - Live stock data
- `/watchlists/` - User watchlists

#### Admin Dashboard

WordPress Admin → Stock Scanner provides:
- Real-time market status indicator
- Scheduler controls
- System health monitoring
- API configuration
- User management

### 🎯 **Production Deployment**

For production use:

1. **Set up proper Cloudflare tunnel domain** (not temporary tunnel)
2. **Configure WordPress cron to run every minute** via hosting provider
3. **Monitor logs regularly** via the management script
4. **Set up hosting provider's cron backup** if WordPress cron fails

#### IONOS Specific Notes

IONOS hosting typically:
- ✅ Supports WordPress cron
- ✅ Allows outgoing HTTP requests
- ✅ Provides adequate PHP memory limits
- ⚠️ May have execution time limits (usually 30-60 seconds)

### 🔄 **Regular Maintenance**

#### Daily Monitoring

```bash
# Quick status check
php manage_scheduler_windows.php status

# Check logs for errors
php manage_scheduler_windows.php logs
```

#### Weekly System Check

```bash
# Comprehensive diagnostics
php manage_scheduler_windows.php syscheck
```

This system is designed to be **set-and-forget** once properly configured, with intelligent market hours management and robust error handling suitable for production hosting environments.