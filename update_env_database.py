#!/usr/bin/env python3
"""
Update .env Database Configuration Script
Automatically updates .env file with PostgreSQL credentials.

Usage:
    python update_env_database.py

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
from pathlib import Path

def update_env_file():
    """Update .env file with PostgreSQL configuration"""
    print("🔧 Updating .env file with database configuration...")
    
    env_file = Path(".env")
    
    # Database configuration
    db_config = {
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'stockscanner_prod',
        'DB_USER': 'stockscanner',
        'DB_PASSWORD': 'C2rt3rK#2010',
        'DATABASE_URL': 'postgresql://stockscanner:C2rt3rK#2010@localhost:5432/stockscanner_prod'
    }
    
    # Read existing .env file if it exists
    existing_config = {}
    if env_file.exists():
        print("📄 Reading existing .env file...")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    existing_config[key] = value
    
    # Update with database configuration
    existing_config.update(db_config)
    
    # Write updated .env file
    print("💾 Writing updated .env file...")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("# Stock Scanner Environment Configuration\n")
        f.write("# Updated automatically with database credentials\n\n")
        
        # Production settings
        f.write("# Production Environment\n")
        f.write("DEBUG=False\n")
        f.write("SECRET_KEY=your-super-secret-key-here-make-it-long-and-random\n")
        f.write("ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,www.your-domain.com\n\n")
        
        # Database configuration
        f.write("# Database Configuration\n")
        for key, value in db_config.items():
            f.write(f"{key}={value}\n")
        f.write("\n")
        
        # Other configurations
        f.write("# Redis Configuration\n")
        f.write("REDIS_URL=redis://localhost:6379/0\n")
        f.write("CELERY_BROKER_URL=redis://localhost:6379/0\n")
        f.write("CELERY_RESULT_BACKEND=redis://localhost:6379/0\n\n")
        
        f.write("# Email Configuration\n")
        f.write("EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend\n")
        f.write("EMAIL_HOST=smtp.your-email-provider.com\n")
        f.write("EMAIL_PORT=587\n")
        f.write("EMAIL_USE_TLS=True\n")
        f.write("EMAIL_HOST_USER=your-email@domain.com\n")
        f.write("EMAIL_HOST_PASSWORD=your-email-password\n\n")
        
        f.write("# Payment Configuration\n")
        f.write("STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key\n")
        f.write("STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key\n")
        f.write("STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret\n\n")
        
        f.write("# Yahoo Finance API Configuration\n")
        f.write("STOCK_API_RATE_LIMIT=1.0\n")
        f.write("YFINANCE_THREADS=5\n\n")
        
        f.write("# Static Files\n")
        f.write("STATIC_URL=/static/\n")
        f.write("MEDIA_URL=/media/\n")
    
    print("✅ .env file updated successfully!")
    print()
    print("📋 Database configuration:")
    print("   Host: localhost")
    print("   Port: 5432")
    print("   Database: stockscanner_prod")
    print("   Username: stockscanner")
    print("   Password: C2rt3rK#2010")
    
    return True

def main():
    """Main function"""
    print("🔧 Database Configuration Updater")
    print("=" * 40)
    print()
    print("This script will update your .env file with the correct")
    print("PostgreSQL database configuration.")
    print()
    
    try:
        if update_env_file():
            print("\n✅ SUCCESS: .env file updated!")
            print("\n📋 Next steps:")
            print("   python manage.py migrate")
            print("   python manage.py createsuperuser")
            print("   python manage.py runserver")
        else:
            print("\n❌ FAILED: Could not update .env file")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()