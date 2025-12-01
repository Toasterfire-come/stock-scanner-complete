#!/bin/bash
export DJANGO_SETTINGS_MODULE=stockscanner_django.settings_local_sqlite
cd /app/backend
python manage.py runserver 0.0.0.0:8001
