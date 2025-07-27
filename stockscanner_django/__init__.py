"""
Stock Scanner Django Project Initialization
Auto-configures for XAMPP MySQL compatibility
"""

import os
import sys

# Add XAMPP MySQL to PATH if it exists
XAMPP_MYSQL_PATH = r"C:\xampp\mysql\bin"
if os.path.exists(XAMPP_MYSQL_PATH) and XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
    os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH

# Configure PyMySQL for MySQL compatibility
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Only import Celery if explicitly enabled
if os.environ.get('CELERY_ENABLED', 'false').lower() == 'true':
    try:
        from .celery import app as celery_app
        __all__ = ("celery_app",)
    except Exception:
        # If Celery import fails, continue without it
        pass
else:
    # Development mode - no Celery
    pass
