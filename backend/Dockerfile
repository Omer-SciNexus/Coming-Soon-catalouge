# Django + Wagtail API and admin. Build context is the project root,
# because the app reads the sample files in data/ (see DEMO_DATA_DIR).
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data /app/data
COPY backend .

# Admin CSS/JS go into STATIC_ROOT; WhiteNoise serves them.
RUN python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["sh", "docker-entrypoint.sh"]
