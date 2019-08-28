web: gunicorn speckbit_bot.wsgi
worker: celery -A speckbit_bot worker -l debug
beat: celery -A speckbit_bot beat -l debug