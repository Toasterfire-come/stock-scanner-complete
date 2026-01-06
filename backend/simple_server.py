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
    host = os.environ.get("BIND_HOST", "127.0.0.1")
    port = int(os.environ.get("BIND_PORT", "8001"))
    server = simple_server.make_server(host, port, application)
    print(f"Django server running on http://{host}:{port}/")
    print("Use Ctrl+C to quit.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        server.shutdown()