release: python manage.py migrate
web: gunicorn config.wsgi:application
worker: celery worker --beat --app=capitolzen.tasks --loglevel=info
