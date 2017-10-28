release: python manage.py migrate
web: gunicorn config.wsgi:application
worker: celery worker --beat --app=capitolzen.tasks --loglevel=info
tika: java -jar /tika-server-1.16.jar -h 0.0.0.0