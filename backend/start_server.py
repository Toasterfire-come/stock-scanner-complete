#!/usr/bin/env python
"""
Simple Django development server startup script
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
os.environ.setdefault('DB_ENGINE', 'django.db.backends.sqlite3')
os.environ.setdefault('DEBUG', 'True')

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8001'])