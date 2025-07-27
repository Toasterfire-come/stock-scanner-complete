#!/bin/bash

# Set environment variables for Django to use correct MySQL settings
echo "Setting Django environment variables for correct MySQL configuration..."

export DB_ENGINE='django.db.backends.mysql'
export DB_NAME='stockscanner'
export DB_USER='root'
export DB_PASSWORD=''
export DB_HOST='localhost'
export DB_PORT='3306'

echo "Environment variables set:"
echo "DB_ENGINE=$DB_ENGINE"
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=(empty)"
echo "DB_HOST=$DB_HOST"
echo "DB_PORT=$DB_PORT"
echo ""
echo "Now you can run Django commands that will use these settings:"
echo "python3 manage.py migrate"
echo "python3 manage.py runserver"
echo ""
echo "To use these settings permanently, add this to your ~/.bashrc:"
echo "source $(pwd)/set_django_env.sh"