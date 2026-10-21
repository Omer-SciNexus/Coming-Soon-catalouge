#!/bin/sh
# Runs once, when the Codespace is created. Each step is safe to repeat.
set -e

pip install -r backend/requirements.txt
(cd frontend && npm ci)

cd backend
python manage.py migrate --noinput
python manage.py seed_demo

# Demo admin login. The ports are private, so only your GitHub account can open the admin.
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@example.invalid \
DJANGO_SUPERUSER_PASSWORD=demo-admin-password \
  python manage.py createsuperuser --noinput 2>/dev/null || true
