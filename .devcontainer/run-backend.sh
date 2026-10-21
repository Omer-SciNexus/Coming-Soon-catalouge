#!/bin/sh
# Starts Django with auto-reload. In Codespaces, "View live" in Wagtail must open the
# forwarded https URL of port 3000, not localhost.
if [ -n "$CODESPACE_NAME" ]; then
  export FRONTEND_URL="https://$CODESPACE_NAME-3000.$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
fi

cd backend
exec python manage.py runserver 127.0.0.1:8000
