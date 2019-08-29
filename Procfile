web: gunicorn speckbit_bot.wsgi
worker: python manage.py celery worker --loglevel=info --beat