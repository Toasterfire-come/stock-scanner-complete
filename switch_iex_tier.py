#!/usr/bin/env python3
"""
Easy IEX Cloud Tier Switching Script
Allows quick switching between free and paid IEX tiers
"""

import os
import sys
import subprocess

def get_current_tier():
    """Get current IEX tier from environment"""
    # Check .env file
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip().startswith('IEX_TIER='):
                    return line.strip().split('=')[1]
                elif line.strip().startswith('IEX_API_KEY='):
                    key = line.strip().split('=')[1]
                    if key.startswith('pk_test_'):
                        return 'free'
                    elif key.startswith('pk_'):
                        return 'paid (auto-detected)'
    
    return 'free (default)'

def update_env_file(tier):
    """Update .env file with new tier"""
    env_file = '.env'
    lines = []
    tier_found = False
    
    # Read existing lines
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Update or add IEX_TIER line
    with open(env_file, 'w') as f:
        for line in lines:
            if line.strip().startswith('IEX_TIER='):
                f.write(f'IEX_TIER={tier}\n')
                tier_found = True
            else:
                f.write(line)
        
        # Add tier if not found
        if not tier_found:
            f.write(f'\n# IEX Cloud Tier\nIEX_TIER={tier}\n')

def restart_service():
    """Restart the NASDAQ collection service"""
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'nasdaq-complete-collector.service'], 
                      check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def test_collection():
    """Run a test collection to verify tier"""
    try:
        result = subprocess.run(['python', 'manage.py', 'collect_nasdaq_realtime', '--once'], 
                               capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Test failed"

def main():
    tiers = {
        '1': ('free', '$0/month - 78.5% coverage (2,614 stocks)'),
        '2': ('start', '$9/month - 100% coverage (3,331 stocks)'),
        '3': ('launch', '$19/month - 100% coverage + 10x faster'),
        '4': ('grow', '$99/month - 100% coverage + 20x faster'),
        '5': ('scale', '$199/month - 100% coverage + 100x faster'),
        '6': ('enterprise', '$999/month - 100% coverage + 1000x faster')
    }
    
    print("🚀 IEX Cloud Tier Switching Tool")
    print("=" * 50)
    
    current = get_current_tier()
    print(f"📊 Current tier: {current}")
    print()
    
    print("�� Available tiers:")
    for key, (tier, desc) in tiers.items():
        print(f"   {key}. {tier:10} - {desc}")
    print()
    
    # Get user choice
    choice = input("🎯 Select tier (1-6) or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        print("👋 Goodbye!")
        return
    
    if choice not in tiers:
        print("❌ Invalid choice")
        return
    
    tier, desc = tiers[choice]
    
    print(f"\n🔄 Switching to {tier} tier...")
    print(f"💰 Cost: {desc}")
    
    # Confirm if switching to paid tier
    if tier != 'free' and current.startswith('free'):
        print(f"\n⚠️ You are switching from FREE to PAID tier!")
        print(f"💳 Make sure you have:")
        print(f"   1. Signed up at https://iexcloud.io/pricing")
        print(f"   2. Updated IEX_API_KEY in .env with your paid key")
        print(f"   3. Billing configured for ${desc.split()[0].replace('$', '')}")
        
        confirm = input(f"\n✅ Continue with {tier} tier? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Cancelled")
            return
    
    # Update .env file
    update_env_file(tier)
    print(f"✅ Updated .env file with IEX_TIER={tier}")
    
    # Restart service
    print("🔄 Restarting collection service...")
    if restart_service():
        print("✅ Service restarted successfully")
    else:
        print("⚠️ Could not restart service automatically")
        print("💡 Run manually: sudo systemctl restart nasdaq-complete-collector.service")
    
    # Test collection
    print("🧪 Testing new configuration...")
    success, output = test_collection()
    
    if success:
        print("✅ Test successful!")
        
        # Parse output for key information
        if "🎉 FULL NASDAQ COVERAGE ACHIEVED!" in output:
            print("🎉 100% NASDAQ coverage confirmed!")
        elif "stocks (" in output:
            # Extract coverage info
            for line in output.split('\n'):
                if 'Coverage:' in line and 'stocks' in line:
                    print(f"📊 {line.strip()}")
                    break
        
        # Show tier info
        for line in output.split('\n'):
            if 'IEX Tier:' in line:
                print(f"💎 {line.strip()}")
                break
    else:
        print("❌ Test failed - check logs for details")
        print("💡 Run: python manage.py collect_nasdaq_realtime --once")
    
    print(f"\n🎯 Tier switch complete!")
    print(f"📊 Monitor: sudo journalctl -u nasdaq-complete-collector.service -f")

if __name__ == "__main__":
    main()
