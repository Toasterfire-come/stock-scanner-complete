#!/usr/bin/env python3
"""
Production Deployment Verification
Checks if the Stock Scanner is ready for production deployment.
"""

import os
import sys
from pathlib import Path

def check_production_readiness():
    """Check if the application is production ready"""
    print("🔍 Production Readiness Check")
    print("=" * 40)
    
    issues = []
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        if 'DEBUG=true' in env_content or 'DEBUG=True' in env_content:
            issues.append("❌ DEBUG is enabled (should be false for production)")
        
        if 'your-' in env_content or 'change-this' in env_content:
            issues.append("❌ Placeholder values found in .env file")
        
        if 'ALLOWED_HOSTS=*' in env_content:
            issues.append("❌ ALLOWED_HOSTS allows all hosts (security risk)")
    else:
        issues.append("❌ .env file not found")
    
    # Check SECRET_KEY
    if 'django-insecure' in env_content:
        issues.append("❌ Using default/insecure SECRET_KEY")
    
    # Check database configuration
    if 'sqlite' in env_content.lower():
        issues.append("⚠️  Using SQLite (consider MySQL for production)")
    
    # Check static files
    static_dir = Path('staticfiles')
    if not static_dir.exists():
        issues.append("⚠️  Static files not collected (run collectstatic)")
    
    # Report results
    if not issues:
        print("✅ All checks passed! Ready for production.")
        return True
    else:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False

if __name__ == "__main__":
    ready = check_production_readiness()
    sys.exit(0 if ready else 1)
