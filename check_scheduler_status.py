#!/usr/bin/env python3
"""
Check Stock Scheduler Status
Simple script to check if the background scheduler is running
"""

import os
import sys
import psutil
import time
from pathlib import Path
from datetime import datetime

def find_scheduler_processes():
    """Find running scheduler processes"""
    scheduler_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if 'start_stock_scheduler' in cmdline and 'python' in proc.info['name'].lower():
                scheduler_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline,
                    'create_time': datetime.fromtimestamp(proc.create_time())
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return scheduler_processes

def check_log_files():
    """Check scheduler log files for recent activity"""
    log_files = [
        'stock_scheduler.log',
        'stock_scheduler_background.log', 
        'windows_scheduler_background.log'
    ]
    
    recent_logs = []
    for log_file in log_files:
        log_path = Path(log_file)
        if log_path.exists():
            stat = log_path.stat()
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            recent_logs.append({
                'file': log_file,
                'size': stat.st_size,
                'modified': modified_time,
                'recent': (datetime.now() - modified_time).seconds < 300  # 5 minutes
            })
    
    return recent_logs

def main():
    """Main status check function"""
    print("STOCK SCHEDULER STATUS CHECK")
    print("=" * 50)
    print(f"Check time: {datetime.now()}")
    print()
    
    # Check for running processes
    processes = find_scheduler_processes()
    
    if processes:
        print(f"[RUNNING] Found {len(processes)} scheduler process(es):")
        for proc in processes:
            print(f"  PID: {proc['pid']}")
            print(f"  Name: {proc['name']}")
            print(f"  Started: {proc['create_time']}")
            print(f"  Command: {proc['cmdline'][:100]}...")
            print()
    else:
        print("[STOPPED] No scheduler processes found")
        print()
    
    # Check log files
    logs = check_log_files()
    
    if logs:
        print("LOG FILE STATUS:")
        for log in logs:
            status = "[ACTIVE]" if log['recent'] else "[INACTIVE]"
            print(f"  {status} {log['file']}")
            print(f"    Size: {log['size']} bytes")
            print(f"    Modified: {log['modified']}")
            print()
    else:
        print("[NO LOGS] No scheduler log files found")
        print()
    
    # Overall status
    is_running = len(processes) > 0
    has_recent_activity = any(log['recent'] for log in logs)
    
    if is_running and has_recent_activity:
        print("[SUCCESS] Scheduler is RUNNING and ACTIVE")
    elif is_running:
        print("[WARNING] Scheduler process found but no recent log activity")
    elif has_recent_activity:
        print("[WARNING] Recent log activity but no process found")
    else:
        print("[ERROR] Scheduler appears to be STOPPED")
    
    print()
    print("COMMANDS:")
    print("  Start: python start_stock_scheduler.py --background")
    print("  Start (Windows): start_scheduler_background.bat")
    print("  Stop: Use Task Manager to end Python processes")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[STOP] Status check interrupted")
    except Exception as e:
        print(f"\n[ERROR] Status check failed: {e}")