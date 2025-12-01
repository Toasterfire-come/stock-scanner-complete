"""
Django ASGI application entry point for uvicorn
"""
import os
import sys
from pathlib import Path

# Add backend to path first
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / '.env')
except ImportError:
    pass

# Set Django settings module - MUST be set before any Django imports
# Use environment variable or default to SQLite local settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings_local_sqlite')

# Configure PyMySQL (if needed, but we use SQLite)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Import Django ASGI application
import django
django.setup()

from django.core.asgi import get_asgi_application
app = get_asgi_application()
