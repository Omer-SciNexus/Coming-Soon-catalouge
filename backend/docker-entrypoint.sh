#!/bin/sh
# Runs every time the backend container starts. Each step is safe to repeat.
set -e

python manage.py migrate --noinput
python manage.py seed_demo

# Creates the admin user from DJANGO_SUPERUSER_* variables; fails harmlessly if it already exists.
python manage.py createsuperuser --noinput 2>/dev/null || true

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile -
