@echo off
REM ============================================================
REM Daily Scanner Runner - FAST (5 HOUR TARGET)
REM ============================================================
REM Production version with:
REM - 304 proxy rotation
REM - 0.488 t/s rate limiting (2.05 seconds per request)
REM - 20 threads (parallel processing)
REM - Completes 8782 stocks in EXACTLY 5 hours
REM ============================================================

cd /d "%~dp0"
python3 realtime_daily_with_proxies.py >> logs\daily_scanner.log 2>&1
