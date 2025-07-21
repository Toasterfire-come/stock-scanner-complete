# Local Database Configuration for Stock Scanner
# Using SQLite for local development and deployment

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# Local SQLite Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'stock_scanner.db',
        'OPTIONS': {
            'timeout': 20,  # 20 seconds timeout for database operations
        },
        'ATOMIC_REQUESTS': True,  # Database transactions
    }
}

# Database connection settings for SQLite
DATABASE_SETTINGS = {
    'engine': 'sqlite3',
    'name': 'stock_scanner.db',
    'path': str(BASE_DIR / 'stock_scanner.db'),
    'backup_path': str(BASE_DIR / 'backups'),
    'max_size_mb': 100,  # Maximum database size in MB
}

# SQLite specific optimizations
SQLITE_OPTIMIZATIONS = {
    'journal_mode': 'WAL',  # Write-Ahead Logging for better concurrency
    'synchronous': 'NORMAL',  # Balance between safety and speed
    'cache_size': 2000,  # Cache size in pages
    'temp_store': 'MEMORY',  # Store temporary tables in memory
    'mmap_size': 268435456,  # 256MB memory-mapped I/O
}

def optimize_sqlite_database():
    """Apply SQLite optimizations for better performance"""
    import sqlite3
    
    db_path = DATABASE_SETTINGS['path']
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Apply optimizations
        cursor.execute(f"PRAGMA journal_mode = {SQLITE_OPTIMIZATIONS['journal_mode']}")
        cursor.execute(f"PRAGMA synchronous = {SQLITE_OPTIMIZATIONS['synchronous']}")
        cursor.execute(f"PRAGMA cache_size = {SQLITE_OPTIMIZATIONS['cache_size']}")
        cursor.execute(f"PRAGMA temp_store = {SQLITE_OPTIMIZATIONS['temp_store']}")
        cursor.execute(f"PRAGMA mmap_size = {SQLITE_OPTIMIZATIONS['mmap_size']}")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_stock_ticker ON stocks_stockalert(ticker)",
            "CREATE INDEX IF NOT EXISTS idx_stock_last_update ON stocks_stockalert(last_update)",
            "CREATE INDEX IF NOT EXISTS idx_email_category ON emails_emailsubscription(category)",
            "CREATE INDEX IF NOT EXISTS idx_email_active ON emails_emailsubscription(is_active)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError:
                pass  # Index might already exist or table might not exist yet
        
        connection.commit()
        connection.close()
        
        print("✅ SQLite database optimized successfully")
        return True
        
    except Exception as e:
        print(f"❌ SQLite optimization failed: {e}")
        return False

def backup_sqlite_database():
    """Create a backup of the SQLite database"""
    import shutil
    from datetime import datetime
    
    db_path = DATABASE_SETTINGS['path']
    backup_dir = Path(DATABASE_SETTINGS['backup_path'])
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"stock_scanner_backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename
    
    try:
        if Path(db_path).exists():
            shutil.copy2(db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return str(backup_path)
        else:
            print("⚠️ Database file does not exist yet")
            return None
            
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def get_database_size():
    """Get the current size of the SQLite database"""
    db_path = Path(DATABASE_SETTINGS['path'])
    
    if db_path.exists():
        size_bytes = db_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        return {
            'size_bytes': size_bytes,
            'size_mb': round(size_mb, 2),
            'size_formatted': f"{size_mb:.2f} MB"
        }
    else:
        return {
            'size_bytes': 0,
            'size_mb': 0,
            'size_formatted': "0 MB"
        }

def check_database_health():
    """Check SQLite database health and integrity"""
    import sqlite3
    
    db_path = DATABASE_SETTINGS['path']
    
    if not Path(db_path).exists():
        return {'healthy': False, 'message': 'Database file does not exist'}
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Check integrity
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        # Get database info
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchall()
        
        # Get table count
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        connection.close()
        
        health_info = {
            'healthy': integrity_result == 'ok',
            'integrity': integrity_result,
            'tables': table_count,
            'size': get_database_size(),
            'message': 'Database is healthy' if integrity_result == 'ok' else f'Integrity check failed: {integrity_result}'
        }
        
        return health_info
        
    except Exception as e:
        return {'healthy': False, 'message': f'Health check failed: {e}'}

def vacuum_database():
    """Vacuum the SQLite database to reclaim space"""
    import sqlite3
    
    db_path = DATABASE_SETTINGS['path']
    
    try:
        connection = sqlite3.connect(db_path)
        connection.execute("VACUUM")
        connection.close()
        
        print("✅ Database vacuumed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database vacuum failed: {e}")
        return False

# Cache configuration for local development
LOCAL_CACHE_CONFIG = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'stock-scanner-cache',
        'TIMEOUT': 300,  # 5 minutes default timeout
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

def get_local_database_config():
    """Get complete database configuration for local development"""
    return {
        'DATABASES': DATABASES,
        'CACHES': LOCAL_CACHE_CONFIG,
        'database_settings': DATABASE_SETTINGS,
        'optimizations': SQLITE_OPTIMIZATIONS,
    }

# Test database connection
def test_database_connection():
    """Test SQLite database connection"""
    import sqlite3
    
    db_path = DATABASE_SETTINGS['path']
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        connection.close()
        
        if result:
            return True, "SQLite database connection successful"
        else:
            return False, "SQLite database connection failed - no result"
            
    except Exception as e:
        return False, f"SQLite database connection failed: {str(e)}"

# Django management commands helper
def setup_local_database():
    """Setup local SQLite database with optimizations"""
    print("🗄️ Setting up local SQLite database...")
    
    # Test connection
    success, message = test_database_connection()
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        return False
    
    # Apply optimizations
    if optimize_sqlite_database():
        print("✅ Database optimized")
    
    # Check health
    health = check_database_health()
    if health['healthy']:
        print(f"✅ Database health check passed - {health['size']['size_formatted']}")
    else:
        print(f"⚠️ Database health check: {health['message']}")
    
    return True

if __name__ == "__main__":
    # Run setup when called directly
    setup_local_database()