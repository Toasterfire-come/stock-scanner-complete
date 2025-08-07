# Market Hours Manager

The Market Hours Manager is an automated system that starts and stops all stock scanner components based on market hours. It ensures that your stock scanner runs efficiently during trading hours and conserves resources when markets are closed.

## Features

- **Automatic Market Hours Detection**: Uses Eastern Time to determine market phases
- **Component Management**: Starts/stops retrieval script, news scraper, emails, and server
- **Graceful Process Management**: Properly terminates processes with timeout handling
- **Health Monitoring**: Monitors component health and restarts failed processes
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Market Hours Schedule

| Phase | Time (ET) | Active Components |
|-------|-----------|-------------------|
| **Premarket** | 4:00 AM - 9:30 AM | Stock Retrieval, News Scraper, Emails |
| **Market** | 9:30 AM - 4:00 PM | All Components + Django Server |
| **Postmarket** | 4:00 PM - 8:00 PM | Stock Retrieval, News Scraper, Emails |
| **After Hours** | 8:00 PM - 4:00 AM | All Components Stopped |

*Note: No components run on weekends (Saturday/Sunday)*

## Components Managed

### 1. Stock Retrieval (`enhanced_stock_retrieval_working.py`)
- **Purpose**: Fetches real-time stock data from Yahoo Finance
- **Schedule**: Runs continuously during premarket, market, and postmarket hours
- **Database**: Stores data in Django database

### 2. News Scraper (`python manage.py scrape_news`)
- **Purpose**: Scrapes Yahoo Finance news feeds
- **Schedule**: Runs every 5 minutes during active hours
- **Database**: Stores articles with sentiment analysis

### 3. Email Sender (`python manage.py send_stock_emails`)
- **Purpose**: Sends personalized stock alerts to subscribers
- **Schedule**: Runs every 10 minutes during active hours
- **Features**: Rate limiting and error handling

### 4. Django Server (`python manage.py runserver`)
- **Purpose**: Web interface and API server
- **Schedule**: Only runs during regular market hours (9:30 AM - 4:00 PM ET)
- **Port**: 0.0.0.0:8000 (accessible from all interfaces)

## Quick Start

### Linux/macOS
```bash
# Make executable (first time only)
chmod +x start_market_hours.sh

# Start the manager
./start_market_hours.sh
```

### Windows
```cmd
# Run the batch file
start_market_hours.bat
```

### Python Direct
```bash
# Install dependencies
pip install pytz psutil schedule

# Run directly
python market_hours_manager.py
```

## Installation

### Prerequisites
- Python 3.8+
- Django project (with `manage.py`)
- Required Python packages (auto-installed by scripts)

### Required Packages
The manager will automatically install these if missing:
- `pytz` - Timezone handling
- `psutil` - Process management
- `schedule` - Task scheduling

### Manual Installation
```bash
pip install pytz psutil schedule
```

## Configuration

The manager is pre-configured with standard market hours, but you can modify the `MarketHoursManager` class in `market_hours_manager.py`:

```python
# Market hours configuration
self.premarket_start = "04:00"  # 4:00 AM ET
self.market_open = "09:30"      # 9:30 AM ET
self.market_close = "16:00"     # 4:00 PM ET
self.postmarket_end = "20:00"   # 8:00 PM ET
```

### Component Configuration
Each component can be customized in the `self.components` dictionary:

```python
'news_scraper': {
    'command': ['python', 'manage.py', 'scrape_news'],
    'args': [],
    'active_during': ['premarket', 'market', 'postmarket'],
    'process': None,
    'interval': 300  # Run every 5 minutes
}
```

## Usage

### Starting the Manager
The manager will:
1. Check your environment and install missing packages
2. Detect the current market phase
3. Start appropriate components
4. Display a status dashboard
5. Run continuously until stopped

### Stopping the Manager
- **Graceful**: Press `Ctrl+C` to stop all components gracefully
- **Force**: Kill the process (components will stop but may not clean up properly)

### Monitoring
- **Console Output**: Real-time status updates
- **Log File**: `market_hours_manager.log` contains detailed logs
- **Status Display**: Updates every 5 minutes showing component status

## Status Dashboard

```
============================================================
MARKET HOURS MANAGER - STATUS
============================================================
Current Time (ET): 2024-01-15 10:30:00 EST
Market Phase: MARKET
------------------------------------------------------------
Component Status:
  stock_retrieval      | RUNNING  | SHOULD RUN
  news_scraper         | STOPPED  | SHOULD RUN
  email_sender         | STOPPED  | SHOULD RUN
  django_server        | RUNNING  | SHOULD RUN
============================================================
```

## Logging

### Log Levels
- **INFO**: Normal operations, component starts/stops
- **WARNING**: Non-critical issues, component restarts
- **ERROR**: Critical issues, component failures

### Log Files
- `market_hours_manager.log` - Main manager log
- `enhanced_stock_retrieval_working.log` - Stock retrieval log
- Individual component logs in their respective directories

## Troubleshooting

### Common Issues

#### 1. "Python not found"
**Solution**: Install Python and add to PATH
```bash
# Linux/macOS
sudo apt install python3  # or brew install python3

# Windows
# Download from python.org and check "Add to PATH"
```

#### 2. "manage.py not found"
**Solution**: Run from Django project root directory
```bash
cd /path/to/your/django/project
./start_market_hours.sh
```

#### 3. "Component failed to start"
**Solutions**:
- Check component logs for specific errors
- Verify database connectivity
- Check file permissions
- Ensure all dependencies are installed

#### 4. "Database connection error"
**Solutions**:
- Verify Django settings.py database configuration
- Check if database server is running
- Test connection manually: `python manage.py dbshell`

### Debug Mode
For detailed debugging, modify the logging level in `market_hours_manager.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Configuration

### Custom Market Hours
To support international markets or custom trading hours:

```python
# Example: London Stock Exchange
self.premarket_start = "07:00"  # 7:00 AM GMT
self.market_open = "08:00"      # 8:00 AM GMT
self.market_close = "16:30"     # 4:30 PM GMT
self.postmarket_end = "17:30"   # 5:30 PM GMT

# Update timezone
self.timezone = pytz.timezone('Europe/London')
```

### Adding Custom Components
```python
'custom_component': {
    'command': ['python', 'my_script.py'],
    'args': ['--production'],
    'active_during': ['market'],
    'process': None,
    'interval': 900  # Run every 15 minutes
}
```

### Environment Variables
Set these in your environment or `.env` file:
```bash
DJANGO_SETTINGS_MODULE=stockscanner_django.settings
DEBUG=False
MARKET_HOURS_LOG_LEVEL=INFO
```

## Production Deployment

### Systemd Service (Linux)
Create `/etc/systemd/system/market-hours-manager.service`:
```ini
[Unit]
Description=Stock Scanner Market Hours Manager
After=network.target

[Service]
Type=simple
User=stockscanner
WorkingDirectory=/path/to/stockscanner
ExecStart=/path/to/stockscanner/start_market_hours.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable market-hours-manager
sudo systemctl start market-hours-manager
```

### Windows Service
Use `nssm` (Non-Sucking Service Manager):
```cmd
nssm install MarketHoursManager
nssm set MarketHoursManager Application C:\path\to\python.exe
nssm set MarketHoursManager AppParameters C:\path\to\market_hours_manager.py
nssm set MarketHoursManager AppDirectory C:\path\to\stockscanner
nssm start MarketHoursManager
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "market_hours_manager.py"]
```

## API Integration

The manager can be extended with a REST API for remote control:

```python
# Add to market_hours_manager.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def manager_status(request):
    """API endpoint for manager status"""
    return JsonResponse({
        'market_phase': self.get_current_market_phase(),
        'components': {
            name: {
                'running': self.check_component_health(name),
                'should_run': self.is_component_active(name, self.get_current_market_phase())
            }
            for name in self.components.keys()
        }
    })
```

## Support

For issues, questions, or contributions:
1. Check the logs for specific error messages
2. Verify all prerequisites are met
3. Test components individually before using the manager
4. Review this documentation for configuration options

## License

This Market Hours Manager is part of the Stock Scanner project and follows the same license terms.