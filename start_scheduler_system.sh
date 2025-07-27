#!/bin/bash
echo "========================================"
echo "Stock Scanner (System Python)"
echo "========================================"
echo

# Set environment variables
export DJANGO_SETTINGS_MODULE=stockscanner_django.settings
export PYTHONIOENCODING=utf-8

# Run the scheduler using system Python
"/usr/bin/python3" start_stock_scheduler.py
