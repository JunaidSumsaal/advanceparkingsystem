#!/bin/bash
python manage.py migrate --noinput
exec gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120
