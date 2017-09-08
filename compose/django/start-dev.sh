#!/bin/sh
rm -rf /app/celerybeat.pid
python manage.py migrate
python manage.py search_index --rebuild
python manage.py runserver_plus 0.0.0.0:8000
