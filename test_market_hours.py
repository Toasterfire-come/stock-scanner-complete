#!/usr/bin/env python3
"""
Test script to verify market hours configuration
Tests that updates only run during regular market hours (9:30 AM - 4:00 PM ET)
"""

import sys
import os
from datetime import datetime, time
import pytz

# Add workspace to path
sys.path.insert(0, '/workspace')

def test_market_hours():
    """Test the market hours logic"""
    eastern_tz = pytz.timezone('US/Eastern')
    
    # Market hours configuration - ONLY REGULAR HOURS
    MARKET_OPEN = "09:30"
    MARKET_CLOSE = "16:00"
    
    print("=" * 60)
    print("MARKET HOURS CONFIGURATION TEST")
    print("=" * 60)
    print(f"Market Open:  {MARKET_OPEN} ET")
    print(f"Market Close: {MARKET_CLOSE} ET")
    print("=" * 60)
    
    # Test various times
    test_times = [
        ("04:00", "Pre-market (DISABLED)"),
        ("08:00", "Pre-market (DISABLED)"),
        ("09:29", "Just before open"),
        ("09:30", "Market open"),
        ("10:00", "Regular hours"),
        ("12:00", "Midday"),
        ("15:30", "Late afternoon"),
        ("15:59", "Just before close"),
        ("16:00", "Market close"),
        ("16:01", "After close"),
        ("18:00", "Post-market (DISABLED)"),
        ("20:00", "Post-market end (DISABLED)"),
    ]
    
    print("\nTIME CHECKS:")
    print("-" * 40)
    
    for test_time, description in test_times:
        # Check if time is within regular market hours
        is_active = MARKET_OPEN <= test_time < MARKET_CLOSE
        status = "✅ ACTIVE" if is_active else "❌ INACTIVE"
        print(f"{test_time} ET - {description:25} {status}")
    
    print("\n" + "=" * 60)
    
    # Check current time
    now_et = datetime.now(eastern_tz)
    current_time = now_et.strftime("%H:%M")
    current_day = now_et.strftime("%A")
    
    print(f"\nCURRENT STATUS:")
    print(f"Current Time: {current_time} ET")
    print(f"Current Day:  {current_day}")
    
    # Check if it's a weekday
    if now_et.weekday() >= 5:
        print("Status: ❌ MARKET CLOSED (Weekend)")
    elif MARKET_OPEN <= current_time < MARKET_CLOSE:
        print("Status: ✅ MARKET OPEN (Regular Hours)")
    else:
        print("Status: ❌ MARKET CLOSED (Outside Regular Hours)")
    
    print("=" * 60)
    
    # Test the actual market hours manager
    try:
        from market_hours_manager import MarketHoursManager
        
        print("\nTesting MarketHoursManager class...")
        manager = MarketHoursManager()
        phase = manager.get_current_market_phase()
        
        print(f"Market Phase: {phase}")
        
        if phase == 'market':
            print("✅ Components would be ACTIVE")
        else:
            print("❌ Components would be INACTIVE")
            
        # Check component status
        print("\nComponent Status:")
        for component_name in manager.components:
            is_active = manager.is_component_active(component_name, phase)
            status = "✅ ACTIVE" if is_active else "❌ INACTIVE"
            print(f"  {component_name:20} {status}")
            
    except Exception as e:
        print(f"\n⚠️  Could not test MarketHoursManager: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_market_hours()