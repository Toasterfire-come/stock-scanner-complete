@echo off
REM ============================================================================
REM Production Scanner System - Startup Script
REM ============================================================================
REM
REM This script starts the master orchestrator which manages all scanners:
REM   - 1-minute scanner: Real-time price updates via WebSocket (prices only)
REM   - 10-minute scanner: Volume/metrics updates (proxied batch calls)
REM   - Daily scanner: Full data refresh (runs at 4:30 PM ET)
REM
REM The orchestrator automatically:
REM   - Starts scanners at market open (9:30 AM ET)
REM   - Stops scanners at market close (4:00 PM ET)
REM   - Only runs on weekdays (Monday-Friday)
REM   - Restarts crashed scanners automatically
REM
REM ============================================================================

echo.
echo ================================================================================
echo PRODUCTION SCANNER SYSTEM
echo ================================================================================
echo.
echo Starting master orchestrator...
echo.
echo The orchestrator will:
echo   - Monitor market hours (9:30 AM - 4:00 PM ET, weekdays only)
echo   - Start/stop scanners automatically
echo   - Restart crashed scanners
echo   - Run daily scanner at 4:30 PM ET
echo.
echo Press Ctrl+C to stop all scanners
echo.
echo ================================================================================
echo.

python scanner_orchestrator.py

echo.
echo ================================================================================
echo SCANNERS STOPPED
echo ================================================================================
echo.

pause
