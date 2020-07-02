release: python manage.py migrate
web: gunicorn config.wsgi
worker: celery worker -A config -l info