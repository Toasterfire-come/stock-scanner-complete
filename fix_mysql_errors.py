#!/usr/bin/env python3
"""
MySQL Error Diagnostic and Fix Tool
Diagnoses and fixes common MySQL database connectivity and query issues
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_mysql_service():
    """Check if MySQL service is running"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['sc', 'query', 'mysql'], capture_output=True, text=True)
            if 'RUNNING' in result.stdout:
                return True, "MySQL service is running"
            else:
                return False, "MySQL service is not running"
        else:  # Linux/Mac
            result = subprocess.run(['systemctl', 'is-active', 'mysql'], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "MySQL service is active"
            else:
                return False, "MySQL service is not active"
    except Exception as e:
        return False, f"Could not check MySQL service: {e}"

def check_database_connection():
    """Test database connection using Django"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        
        import django
        django.setup()
        
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        return True, "Database connection successful"
        
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"

def fix_mysql_connection_issues():
    """Apply common MySQL connection fixes"""
    fixes_applied = []
    
    try:
        # 1. Update Django settings for better MySQL compatibility
        settings_path = Path('stockscanner_django/settings.py')
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                content = f.read()
            
            # Add MySQL connection optimizations
            mysql_optimizations = """
# MySQL Connection Optimizations
DATABASES['default'].update({
    'OPTIONS': {
        'charset': 'utf8mb4',
        'use_unicode': True,
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'autocommit': True,
        'connect_timeout': 60,
        'read_timeout': 60,
        'write_timeout': 60,
    },
    'CONN_MAX_AGE': 3600,  # 1 hour connection pooling
})
"""
            
            if 'CONN_MAX_AGE' not in content:
                content += mysql_optimizations
                with open(settings_path, 'w') as f:
                    f.write(content)
                fixes_applied.append("Added MySQL connection optimizations to settings.py")
        
        # 2. Create database error handling utility
        db_utils_content = '''"""
Database Utilities for MySQL Error Handling
"""

import logging
import time
from django.db import connection, transaction
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced database manager with error handling"""
    
    @staticmethod
    def safe_execute(query, params=None, retries=3):
        """Execute query with retry logic"""
        for attempt in range(retries):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, params or [])
                    if cursor.description:
                        return cursor.fetchall()
                    return True
            except Exception as e:
                logger.warning(f"Query attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    connection.close()  # Force reconnection
                else:
                    raise
    
    @staticmethod
    def batch_insert_safe(model, objects, batch_size=100):
        """Safe batch insert with error handling"""
        total_inserted = 0
        errors = []
        
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            try:
                with transaction.atomic():
                    model.objects.bulk_create(batch, ignore_conflicts=True)
                total_inserted += len(batch)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
            except Exception as e:
                errors.append(f"Batch {i//batch_size + 1}: {e}")
                logger.error(f"Batch insert failed: {e}")
                
                # Try individual inserts for failed batch
                for obj in batch:
                    try:
                        obj.save()
                        total_inserted += 1
                    except Exception as individual_error:
                        errors.append(f"Individual insert: {individual_error}")
        
        return total_inserted, errors
    
    @staticmethod
    def reconnect_if_needed():
        """Reconnect to database if connection is lost"""
        try:
            connection.ensure_connection()
        except Exception as e:
            logger.warning(f"Database reconnection needed: {e}")
            connection.close()
            connection.connect()
'''
        
        db_utils_path = Path('stocks/db_utils.py')
        with open(db_utils_path, 'w') as f:
            f.write(db_utils_content)
        fixes_applied.append("Created database utilities with error handling")
        
        # 3. Update management command to handle MySQL errors better
        update_command_path = Path('stocks/management/commands/update_stocks_yfinance.py')
        if update_command_path.exists():
            with open(update_command_path, 'r') as f:
                content = f.read()
            
            # Add error handling imports
            if 'from stocks.db_utils import DatabaseManager' not in content:
                content = content.replace(
                    'from django.core.management.base import BaseCommand',
                    'from django.core.management.base import BaseCommand\nfrom stocks.db_utils import DatabaseManager'
                )
                
                # Replace bulk operations with safe operations
                content = content.replace(
                    'Stock.objects.bulk_create(',
                    'DatabaseManager.batch_insert_safe(Stock, '
                )
                
                with open(update_command_path, 'w') as f:
                    f.write(content)
                fixes_applied.append("Updated stock update command with safe database operations")
    
    except Exception as e:
        fixes_applied.append(f"Error applying fixes: {e}")
    
    return fixes_applied

def increase_mysql_timeouts():
    """Increase MySQL timeout values"""
    timeout_fixes = []
    
    try:
        # Create MySQL configuration
        mysql_config = """
[client]
connect_timeout = 60
read_timeout = 60
write_timeout = 60

[mysql]
connect_timeout = 60

[mysqldump]
single-transaction
quick
routines
triggers
"""
        
        config_path = Path('mysql_timeout.cnf')
        with open(config_path, 'w') as f:
            f.write(mysql_config)
        
        timeout_fixes.append(f"Created MySQL timeout configuration: {config_path}")
        
        # Instructions for applying the config
        instructions = """
To apply MySQL timeout fixes:

1. Copy mysql_timeout.cnf to your MySQL configuration directory
2. Or add these settings to your existing my.cnf/my.ini file:
   
   [mysqld]
   connect_timeout = 60
   net_read_timeout = 60
   net_write_timeout = 60
   wait_timeout = 28800
   interactive_timeout = 28800
   
3. Restart MySQL service
4. Alternatively, run these SQL commands:
   SET GLOBAL connect_timeout = 60;
   SET GLOBAL net_read_timeout = 60;
   SET GLOBAL net_write_timeout = 60;
"""
        
        with open('MYSQL_TIMEOUT_INSTRUCTIONS.md', 'w') as f:
            f.write(instructions)
        
        timeout_fixes.append("Created MySQL timeout instructions")
        
    except Exception as e:
        timeout_fixes.append(f"Error creating timeout fixes: {e}")
    
    return timeout_fixes

def main():
    """Main diagnostic and fix function"""
    print("MYSQL ERROR DIAGNOSTIC AND FIX TOOL")
    print("=" * 50)
    print()
    
    # Check MySQL service
    print("[CHECK] MySQL Service Status...")
    service_running, service_msg = check_mysql_service()
    print(f"  {service_msg}")
    print()
    
    # Check database connection
    print("[CHECK] Database Connection...")
    conn_ok, conn_msg = check_database_connection()
    print(f"  {conn_msg}")
    print()
    
    # Apply fixes if needed
    if not conn_ok:
        print("[FIX] Applying MySQL connection fixes...")
        fixes = fix_mysql_connection_issues()
        for fix in fixes:
            print(f"  [APPLIED] {fix}")
        print()
        
        print("[FIX] Setting up MySQL timeout configurations...")
        timeout_fixes = increase_mysql_timeouts()
        for fix in timeout_fixes:
            print(f"  [APPLIED] {fix}")
        print()
    
    # Provide recommendations
    print("RECOMMENDATIONS:")
    print("=" * 50)
    
    if not service_running:
        print("1. START MYSQL SERVICE:")
        if os.name == 'nt':
            print("   net start mysql")
            print("   Or use Services.msc to start MySQL service")
        else:
            print("   sudo systemctl start mysql")
        print()
    
    if not conn_ok:
        print("2. CHECK DATABASE CONFIGURATION:")
        print("   - Verify database credentials in .env file")
        print("   - Ensure database exists and user has permissions")
        print("   - Check MySQL server is accepting connections")
        print()
        
        print("3. INCREASE MYSQL TIMEOUTS:")
        print("   - Apply settings from mysql_timeout.cnf")
        print("   - Restart MySQL service after configuration changes")
        print("   - See MYSQL_TIMEOUT_INSTRUCTIONS.md for details")
        print()
    
    print("4. RETRY SCHEDULER:")
    print("   python start_stock_scheduler.py --background")
    print("   Or: start_scheduler_background.bat")
    print()
    
    # Final status
    if service_running and conn_ok:
        print("[SUCCESS] MySQL is properly configured and connected")
    else:
        print("[ACTION NEEDED] Please address the issues above")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[STOP] Diagnostic interrupted")
    except Exception as e:
        print(f"\n[ERROR] Diagnostic failed: {e}")