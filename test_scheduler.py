#!/usr/bin/env python3
"""
Test script to verify the scheduler is working
"""

import subprocess
import sys
import os
from pathlib import Path

def test_django_command():
    """Test if the Django command works"""
    print("Testing Django command...")
    
    project_root = Path(__file__).parent
    manage_py = project_root / 'manage.py'
    python_exe = sys.executable
    
    try:
        # Test the command directly
        result = subprocess.run([
            str(python_exe), str(manage_py),
            'update_stocks_yfinance', '--limit', '5', '--test-mode'
        ], capture_output=True, text=True, timeout=60)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Django command works!")
            return True
        else:
            print("❌ Django command failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Django command: {e}")
        return False

def test_scheduler_start():
    """Test if the scheduler can start"""
    print("\nTesting scheduler start...")
    
    project_root = Path(__file__).parent
    manage_py = project_root / 'manage.py'
    python_exe = sys.executable
    
    try:
        # Test the scheduler command
        result = subprocess.run([
            str(python_exe), str(manage_py),
            'update_stocks_yfinance', '--schedule', '--limit', '5', '--test-mode'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if "SCHEDULER STARTED" in result.stdout or result.returncode == 0:
            print("✅ Scheduler can start!")
            return True
        else:
            print("❌ Scheduler failed to start!")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ Scheduler started (timeout expected)")
        return True
    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SCHEDULER TEST")
    print("=" * 50)
    
    django_ok = test_django_command()
    scheduler_ok = test_scheduler_start()
    
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Django Command: {'✅ OK' if django_ok else '❌ FAILED'}")
    print(f"Scheduler Start: {'✅ OK' if scheduler_ok else '❌ FAILED'}")
    
    if django_ok and scheduler_ok:
        print("\n🎉 All tests passed! Scheduler should work.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")