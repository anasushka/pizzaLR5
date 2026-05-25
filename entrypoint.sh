#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py seed_data 2>/dev/null || true

exec gunicorn pizzeria.wsgi:application --bind 0.0.0.0:8000
