# Enhanced Stock Retrieval Scripts Guide

## Overview

This guide covers the new enhanced stock retrieval scripts that use the entire NYSE CSV, filter delisted stocks, and support production settings with command line arguments.

## Scripts Available

### 1. `enhanced_stock_retrieval.py` - Standalone Version
- **Purpose**: Standalone script that doesn't require Django setup
- **Use Case**: Quick testing, data collection without database
- **Output**: JSON files only

### 2. `production_stock_retrieval.py` - Django-Integrated Version
- **Purpose**: Full Django integration with database saving
- **Use Case**: Production environments, database updates
- **Output**: JSON files + database storage

## Command Line Arguments

Both scripts support the following arguments:

### Core Arguments
- `-noproxy`: Disable proxy usage (default: proxies enabled)
- `-test`: Test mode - process only first 100 tickers (default: all tickers)
- `-threads <number>`: Number of threads (default: 10)
- `-timeout <seconds>`: Request timeout in seconds (default: 10)
- `-csv <file>`: NYSE CSV file path (default: `flat-ui__data-Fri Aug 01 2025.csv`)
- `-output <file>`: Output JSON file (default: auto-generated timestamp)

### Production-Only Arguments (production_stock_retrieval.py)
- `-save`: Save results to database (default: false)

## Usage Examples

### Basic Usage

#### Test Mode (100 tickers, no proxies)
```bash
# Standalone version
python enhanced_stock_retrieval.py -test -noproxy

# Production version
python production_stock_retrieval.py -test -noproxy
```

#### Full Mode (all tickers, with proxies)
```bash
# Standalone version
python enhanced_stock_retrieval.py

# Production version with database saving
python production_stock_retrieval.py -save
```

### Advanced Usage

#### Custom Configuration
```bash
# Custom threads and timeout
python enhanced_stock_retrieval.py -threads 20 -timeout 15

# Custom CSV file
python enhanced_stock_retrieval.py -csv my_nyse_data.csv

# Custom output file
python enhanced_stock_retrieval.py -output my_results.json
```

#### Production with Database
```bash
# Full production run with database saving
python production_stock_retrieval.py -save -threads 15

# Test production run
python production_stock_retrieval.py -test -save -noproxy
```

## Features

### 1. NYSE CSV Processing
- **Source**: Uses the entire `flat-ui__data-Fri Aug 01 2025.csv` file
- **Filtering**: Automatically filters out:
  - Delisted stocks (Financial Status = 'D')
  - ETFs (ETF = 'Y')
  - Empty symbols
- **Result**: Only active NYSE stocks are processed

### 2. Proxy Management
- **Default**: Proxies are enabled for reliable data fetching
- **Disable**: Use `-noproxy` flag to disable proxy usage
- **Rotation**: Automatic proxy rotation every 200 tickers
- **Fallback**: Continues without proxies if none available

### 3. Multi-threading
- **Default**: 10 threads for parallel processing
- **Customizable**: Use `-threads` argument to adjust
- **Optimization**: Automatic timeout management

### 4. Comprehensive Data Collection
Each stock processed includes:
- **Basic Info**: Symbol, company name, exchange
- **Price Data**: Current price, previous close, open, day high/low
- **Volume Data**: Current volume, average volume, volume ratio
- **Financial Metrics**: Market cap, P/E ratio, dividend yield
- **Technical Data**: 52-week high/low, beta, sector, industry
- **Calculated Fields**: Price changes, change percentages

### 5. Error Handling
- **Timeout Management**: Configurable request timeouts
- **Retry Logic**: Multiple data fetching approaches
- **Graceful Degradation**: Continues processing even if some stocks fail
- **Detailed Logging**: Comprehensive error reporting

## Output Files

### JSON Output Structure
```json
{
  "scan_info": {
    "timestamp": "2025-01-27T10:30:00Z",
    "csv_file": "flat-ui__data-Fri Aug 01 2025.csv",
    "test_mode": false,
    "use_proxies": true,
    "save_to_db": false,
    "threads": 10,
    "timeout": 10,
    "total_symbols": 5000,
    "successful": 4850,
    "failed": 150,
    "success_rate": "97.0%",
    "elapsed_time": "125.5s",
    "rate": "39.8 symbols/sec"
  },
  "stocks": [
    {
      "symbol": "AAPL",
      "company_name": "Apple Inc.",
      "current_price": 175.25,
      "previous_close": 172.15,
      "price_change": 3.10,
      "change_percent": 1.80,
      "volume": 89543210,
      "market_cap": 2850000000000,
      "pe_ratio": 28.45,
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "timestamp": "2025-01-27T10:30:00Z"
    }
  ]
}
```

### Database Integration (Production Script)
When using `-save` flag:
- **Stock Model**: Updates/creates Stock objects
- **Price History**: Creates StockPrice records
- **Comprehensive Fields**: All available data is stored
- **Error Handling**: Database errors are logged but don't stop processing

## Performance Optimization

### Recommended Settings

#### For Testing
```bash
python enhanced_stock_retrieval.py -test -noproxy -threads 5 -timeout 8
```

#### For Production
```bash
python production_stock_retrieval.py -save -threads 15 -timeout 12
```

#### For High-Volume Processing
```bash
python production_stock_retrieval.py -save -threads 20 -timeout 15
```

### Performance Tips
1. **Use proxies** for better reliability (default behavior)
2. **Adjust threads** based on your system capabilities
3. **Monitor timeouts** - increase if you have slow connections
4. **Use test mode** first to verify configuration
5. **Check logs** for any issues or optimization opportunities

## Troubleshooting

### Common Issues

#### 1. CSV File Not Found
```bash
# Check if CSV file exists
ls -la flat-ui__data-Fri Aug 01 2025.csv

# Use custom CSV file
python enhanced_stock_retrieval.py -csv /path/to/your/nyse.csv
```

#### 2. Proxy Issues
```bash
# Disable proxies if having issues
python enhanced_stock_retrieval.py -noproxy
```

#### 3. Database Connection Issues (Production Script)
```bash
# Check Django setup
python manage.py check

# Verify database connection
python manage.py dbshell
```

#### 4. Memory Issues
```bash
# Reduce threads for lower memory usage
python enhanced_stock_retrieval.py -threads 5
```

### Log Files
- **enhanced_stock_retrieval.log**: Standalone script logs
- **production_stock_retrieval.log**: Production script logs
- **stock_scheduler.log**: Background scheduler logs

## Integration with Existing System

### Background Scheduler
The scripts can be integrated with the existing scheduler:

```bash
# Update the scheduler to use the new scripts
python start_stock_scheduler.py --use-enhanced-retrieval
```

### API Integration
The retrieved data is automatically available through:
- **REST API**: `/api/stocks/`
- **Database Queries**: Direct Django model access
- **JSON Files**: Manual analysis and processing

## Monitoring and Analytics

### Success Metrics
- **Success Rate**: Target >95% for production
- **Processing Speed**: Target >30 symbols/sec
- **Data Quality**: Verify price accuracy and completeness

### Monitoring Commands
```bash
# Check recent results
ls -la enhanced_stock_retrieval_*.json

# Monitor database growth
python manage.py shell -c "from stocks.models import Stock; print(Stock.objects.count())"

# Check processing logs
tail -f enhanced_stock_retrieval.log
```

## Future Enhancements

### Planned Features
1. **Real-time Monitoring**: Web dashboard for processing status
2. **Incremental Updates**: Only process changed stocks
3. **Advanced Filtering**: Sector, market cap, volume filters
4. **Alert System**: Notifications for processing issues
5. **Performance Analytics**: Detailed performance metrics

### Customization
The scripts are designed to be easily customizable:
- **Data Sources**: Add new CSV formats
- **Filtering Logic**: Modify stock filtering criteria
- **Output Formats**: Add new export formats
- **Integration**: Connect to other systems

## Support

For issues or questions:
1. Check the log files for detailed error messages
2. Verify your CSV file format and content
3. Test with `-test` mode first
4. Review the troubleshooting section above
5. Check the existing documentation for Django setup issues