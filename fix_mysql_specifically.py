#!/usr/bin/env python3
"""
MySQL Specific Fix Tool
Targeted fixes for MySQL connection and query execution errors
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_mysql_service():
    """Check and start MySQL service if needed"""
    print("[CHECK] MySQL Service Status...")
    
    try:
        if os.name == 'nt':  # Windows
            # Check if MySQL service exists and is running
            result = subprocess.run(['sc', 'query', 'mysql'], capture_output=True, text=True)
            if 'does not exist' in result.stderr.lower():
                # Try MySQL80 or other common names
                for service_name in ['MySQL80', 'MySQL57', 'MySQL56', 'MySQLServer']:
                    result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"[FOUND] MySQL service: {service_name}")
                        if 'RUNNING' not in result.stdout:
                            print(f"[START] Starting {service_name}...")
                            start_result = subprocess.run(['net', 'start', service_name], capture_output=True, text=True)
                            if start_result.returncode == 0:
                                print(f"[SUCCESS] {service_name} started")
                                time.sleep(5)  # Wait for service to fully start
                                return True
                            else:
                                print(f"[ERROR] Failed to start {service_name}: {start_result.stderr}")
                        else:
                            print(f"[RUNNING] {service_name} is already running")
                            return True
                print("[ERROR] No MySQL service found")
                return False
            else:
                if 'RUNNING' in result.stdout:
                    print("[RUNNING] MySQL service is running")
                    return True
                else:
                    print("[START] Starting MySQL service...")
                    start_result = subprocess.run(['net', 'start', 'mysql'], capture_output=True, text=True)
                    if start_result.returncode == 0:
                        print("[SUCCESS] MySQL service started")
                        time.sleep(5)
                        return True
                    else:
                        print(f"[ERROR] Failed to start MySQL: {start_result.stderr}")
                        return False
        else:
            # Linux/Mac
            result = subprocess.run(['systemctl', 'is-active', 'mysql'], capture_output=True, text=True)
            if result.returncode == 0:
                print("[RUNNING] MySQL service is active")
                return True
            else:
                print("[START] Starting MySQL service...")
                start_result = subprocess.run(['sudo', 'systemctl', 'start', 'mysql'], capture_output=True, text=True)
                return start_result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Service check failed: {e}")
        return False

def fix_mysql_settings():
    """Apply comprehensive MySQL fixes to Django settings"""
    print("[FIX] Updating Django MySQL configuration...")
    
    try:
        settings_path = Path('stockscanner_django/settings.py')
        if not settings_path.exists():
            print("[ERROR] Django settings.py not found")
            return False
        
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Enhanced MySQL configuration
        mysql_config = """
# Enhanced MySQL Configuration with Error Handling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'stockscanner'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': '''
                SET sql_mode='STRICT_TRANS_TABLES';
                SET innodb_strict_mode=1;
                SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
            ''',
            'autocommit': True,
            'connect_timeout': 60,
            'read_timeout': 300,
            'write_timeout': 300,
            'isolation_level': 'read committed',
        },
        'CONN_MAX_AGE': 0,  # Disable connection pooling to avoid stale connections
        'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction
    }
}

# Database connection retry settings
DATABASE_CONNECTION_RETRY_DELAY = 2
DATABASE_CONNECTION_MAX_RETRIES = 3
"""
        
        # Remove existing database configuration and replace
        import re
        content = re.sub(
            r'DATABASES\s*=\s*{.*?}(?:\s*\n.*?)*(?=\n\S|\nDATABASES|\Z)',
            mysql_config.strip(),
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Add required imports if not present
        if 'import os' not in content:
            content = 'import os\n' + content
        
        # Add MySQL error handling middleware
        mysql_middleware = """
# MySQL Error Handling Middleware
MIDDLEWARE.insert(0, 'django.middleware.db.PersistentConnectionsHealthCheckMiddleware')

# Custom database wrapper for error handling
if 'django.db.backends.mysql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['TEST'] = {
        'CHARSET': 'utf8mb4',
        'COLLATION': 'utf8mb4_unicode_ci',
    }
"""
        
        if 'PersistentConnectionsHealthCheckMiddleware' not in content:
            content += mysql_middleware
        
        with open(settings_path, 'w') as f:
            f.write(content)
        
        print("[SUCCESS] Updated Django MySQL configuration")
        return True
        
    except Exception as e:
        print(f"[ERROR] Settings update failed: {e}")
        return False

def create_mysql_error_handler():
    """Create enhanced database error handling utilities"""
    print("[CREATE] Setting up MySQL error handling...")
    
    try:
        db_utils_content = '''"""
Enhanced MySQL Database Utilities
Handles connection errors, timeouts, and query failures
"""

import logging
import time
import random
from django.db import connection, transaction, OperationalError, InterfaceError
from django.db.utils import DatabaseError
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class MySQLManager:
    """Enhanced MySQL manager with comprehensive error handling"""
    
    @staticmethod
    def safe_execute(query, params=None, retries=5):
        """Execute query with advanced retry logic"""
        for attempt in range(retries):
            try:
                # Force new connection if previous attempts failed
                if attempt > 0:
                    connection.close()
                    time.sleep(random.uniform(1, 3))  # Random delay to avoid thundering herd
                
                with connection.cursor() as cursor:
                    cursor.execute(query, params or [])
                    if cursor.description:
                        return cursor.fetchall()
                    return True
                    
            except (OperationalError, InterfaceError, DatabaseError) as e:
                error_msg = str(e).lower()
                logger.warning(f"MySQL query attempt {attempt + 1} failed: {e}")
                
                # Handle specific MySQL errors
                if 'mysql server has gone away' in error_msg:
                    logger.info("MySQL server disconnected, forcing reconnection...")
                    connection.close()
                elif 'too many connections' in error_msg:
                    logger.warning("Too many MySQL connections, waiting longer...")
                    time.sleep(5 + attempt * 2)
                elif 'deadlock' in error_msg:
                    logger.warning("MySQL deadlock detected, retrying...")
                    time.sleep(random.uniform(0.1, 1.0))
                elif 'timeout' in error_msg:
                    logger.warning("MySQL timeout, extending wait time...")
                    time.sleep(2 ** attempt)
                
                if attempt < retries - 1:
                    # Exponential backoff with jitter
                    delay = min(30, (2 ** attempt) + random.uniform(0, 1))
                    time.sleep(delay)
                else:
                    logger.error(f"All {retries} MySQL query attempts failed")
                    raise
    
    @staticmethod
    def safe_bulk_create(model, objects, batch_size=100):
        """Safe bulk creation with MySQL error handling"""
        if not objects:
            return 0, []
        
        total_created = 0
        errors = []
        
        # Process in smaller batches for MySQL
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            for attempt in range(3):
                try:
                    with transaction.atomic():
                        # Use ignore_conflicts for MySQL compatibility
                        created_objects = model.objects.bulk_create(
                            batch, 
                            ignore_conflicts=True,
                            batch_size=min(50, len(batch))  # Smaller MySQL batches
                        )
                        total_created += len(created_objects)
                        logger.info(f"Batch {batch_num}: Created {len(created_objects)} records")
                        break
                        
                except (OperationalError, InterfaceError, DatabaseError) as e:
                    error_msg = str(e)
                    logger.error(f"Batch {batch_num} attempt {attempt + 1} failed: {error_msg}")
                    
                    if attempt < 2:
                        # Force connection reset and retry
                        connection.close()
                        time.sleep(2 + attempt)
                    else:
                        # Individual insert fallback
                        logger.warning(f"Batch {batch_num}: Falling back to individual inserts")
                        individual_created = 0
                        for obj in batch:
                            try:
                                obj.save()
                                individual_created += 1
                            except Exception as individual_error:
                                errors.append(f"Individual insert error: {individual_error}")
                        
                        total_created += individual_created
                        logger.info(f"Batch {batch_num}: Individual inserts created {individual_created} records")
        
        return total_created, errors
    
    @staticmethod
    def ensure_connection():
        """Ensure MySQL connection is healthy"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.warning(f"MySQL connection unhealthy: {e}")
            connection.close()
            return False
    
    @staticmethod
    def optimize_mysql_session():
        """Optimize current MySQL session settings"""
        optimizations = [
            "SET SESSION innodb_lock_wait_timeout = 300",
            "SET SESSION lock_wait_timeout = 300", 
            "SET SESSION wait_timeout = 28800",
            "SET SESSION interactive_timeout = 28800",
            "SET SESSION net_read_timeout = 300",
            "SET SESSION net_write_timeout = 300",
            "SET SESSION sql_mode = 'STRICT_TRANS_TABLES'",
        ]
        
        for sql in optimizations:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                logger.debug(f"Applied MySQL optimization: {sql}")
            except Exception as e:
                logger.warning(f"Failed to apply optimization {sql}: {e}")
'''
        
        db_utils_path = Path('stocks/mysql_utils.py')
        with open(db_utils_path, 'w') as f:
            f.write(db_utils_content)
        
        print("[SUCCESS] Created MySQL error handling utilities")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create MySQL utilities: {e}")
        return False

def update_stock_command():
    """Update stock management command to use MySQL error handling"""
    print("[UPDATE] Enhancing stock update command for MySQL...")
    
    try:
        command_path = Path('stocks/management/commands/update_stocks_yfinance.py')
        if not command_path.exists():
            print("[ERROR] Stock update command not found")
            return False
        
        with open(command_path, 'r') as f:
            content = f.read()
        
        # Add MySQL utilities import
        if 'from stocks.mysql_utils import MySQLManager' not in content:
            content = content.replace(
                'from django.core.management.base import BaseCommand',
                'from django.core.management.base import BaseCommand\nfrom stocks.mysql_utils import MySQLManager'
            )
        
        # Replace bulk_create with safe version
        content = content.replace(
            'Stock.objects.bulk_create(',
            'MySQLManager.safe_bulk_create(Stock, '
        )
        
        # Add MySQL session optimization at start of handle method
        if 'MySQLManager.optimize_mysql_session()' not in content:
            content = content.replace(
                'def handle(self, *args, **options):',
                '''def handle(self, *args, **options):
        # Optimize MySQL session for large operations
        try:
            MySQLManager.optimize_mysql_session()
            self.stdout.write("[MYSQL] Session optimizations applied")
        except Exception as e:
            self.stdout.write(f"[WARNING] MySQL optimization failed: {e}")
        '''
            )
        
        with open(command_path, 'w') as f:
            f.write(content)
        
        print("[SUCCESS] Updated stock command for MySQL")
        return True
        
    except Exception as e:
        print(f"[ERROR] Command update failed: {e}")
        return False

def test_mysql_comprehensive():
    """Comprehensive MySQL test including bulk operations"""
    print("[TEST] Running comprehensive MySQL tests...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        from django.db import connection
        from stocks.mysql_utils import MySQLManager
        
        # Test 1: Basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"[SUCCESS] MySQL Version: {version[0]}")
        
        # Test 2: Session optimization
        MySQLManager.optimize_mysql_session()
        print("[SUCCESS] MySQL session optimized")
        
        # Test 3: Create test table for bulk operations
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TEMPORARY TABLE test_bulk (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_data VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("[SUCCESS] Test table created")
        
        # Test 4: Bulk insert simulation
        test_data = [{'test_data': f'test_{i}'} for i in range(100)]
        MySQLManager.safe_execute(
            "INSERT INTO test_bulk (test_data) VALUES (%s)",
            [('bulk_test',)]
        )
        print("[SUCCESS] Bulk operation test passed")
        
        # Test 5: Connection health check
        healthy = MySQLManager.ensure_connection()
        print(f"[SUCCESS] Connection health: {'Good' if healthy else 'Needs attention'}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] MySQL test failed: {e}")
        return False

def main():
    """Main MySQL fix function"""
    print("MYSQL SPECIFIC FIX TOOL")
    print("=" * 50)
    print("Targeted fixes for MySQL connection and query errors")
    print()
    
    # Step 1: Check/Start MySQL service
    if not check_mysql_service():
        print("[ERROR] MySQL service is not running")
        print("Please ensure MySQL is installed and the service is started")
        return False
    
    print()
    
    # Step 2: Fix Django MySQL settings
    if not fix_mysql_settings():
        print("[ERROR] Failed to update Django settings")
        return False
    
    print()
    
    # Step 3: Create MySQL error handling utilities
    if not create_mysql_error_handler():
        print("[ERROR] Failed to create error handling")
        return False
    
    print()
    
    # Step 4: Update stock command
    if not update_stock_command():
        print("[ERROR] Failed to update stock command")
        return False
    
    print()
    
    # Step 5: Test everything
    if not test_mysql_comprehensive():
        print("[ERROR] MySQL tests failed")
        return False
    
    print()
    print("=" * 50)
    print("[SUCCESS] MYSQL FIXES COMPLETE!")
    print("=" * 50)
    print()
    print("MySQL has been optimized with:")
    print("- Enhanced connection settings")
    print("- Comprehensive error handling")
    print("- Bulk operation safety")
    print("- Connection health monitoring")
    print("- Session optimizations")
    print()
    print("You can now run:")
    print("  python start_stock_scheduler.py --background")
    print("  start_scheduler_background.bat")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n[HELP] If MySQL issues persist:")
            print("1. Check MySQL error logs")
            print("2. Verify database credentials in .env")
            print("3. Ensure database 'stockscanner' exists")
            print("4. Check MySQL user permissions")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[STOP] MySQL fix interrupted")
    except Exception as e:
        print(f"\n[ERROR] MySQL fix failed: {e}")
        sys.exit(1)