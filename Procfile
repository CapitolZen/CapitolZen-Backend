web: gunicorn config.wsgi:application
worker: celery worker --app=capitolzen.tasks --loglevel=info
