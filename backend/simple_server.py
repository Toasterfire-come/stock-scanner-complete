#!/usr/bin/env python
"""
Simple WSGI server for Django without Uvicorn interference
"""
import os
import sys
from wsgiref import simple_server
import django
from django.core.wsgi import get_wsgi_application

# Set environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
os.environ.setdefault('DB_ENGINE', 'django.db.backends.sqlite3')
os.environ.setdefault('DEBUG', 'True')

# Setup Django
django.setup()

# Get the WSGI application
application = get_wsgi_application()

if __name__ == '__main__':
    # Start the server
    server = simple_server.make_server('0.0.0.0', 8001, application)
    print("Django server running on http://0.0.0.0:8001/")
    print("Use Ctrl+C to quit.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        server.shutdown()