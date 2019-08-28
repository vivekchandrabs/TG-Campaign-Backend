web: gunicorn speckbit_bot.wsgi
worker: celery worker --app=telegram_bot.tasks.app
celery_beat: python manage.py celery beat --loglevel=info