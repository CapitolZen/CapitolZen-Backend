release: python manage.py migrate
web: gunicorn config.wsgi:application --log-file=-
worker: celery worker --beat --app=capitolzen.tasks --loglevel=info
