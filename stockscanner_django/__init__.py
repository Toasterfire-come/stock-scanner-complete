"""
Stock Scanner Django Project Initialization
Auto-configures for XAMPP MySQL compatibility
"""

import os
import sys

# Add XAMPP MySQL to PATH if it exists (Windows only)
import os
import sys

# For Windows XAMPP compatibility
XAMPP_MYSQL_PATH = r"C:\xampp\mysql\bin"
if os.path.exists(XAMPP_MYSQL_PATH) and XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
    os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH

# Configure PyMySQL for MySQL compatibility
# Try to use PyMySQL as MySQLdb replacement
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("INFO: PyMySQL configured as MySQLdb replacement")
except ImportError:
    print("WARNING: PyMySQL not available - falling back to mysqlclient")
    # Try to install PyMySQL if not available
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyMySQL==1.1.0', '--break-system-packages'])
        import pymysql
        pymysql.install_as_MySQLdb()
        print("INFO: PyMySQL installed and configured")
    except Exception as e:
        print(f"WARNING: Could not install/configure PyMySQL: {e}")
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
