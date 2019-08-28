from __future__ import absolute_import

import django
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speckbit_bot.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

django.setup()

app = Celery('speckbit_bot')
# app.conf.broker_url = 'redis://localhost:6379/0'
# app.conf.result_backend = 'redis://localhost:6379/0'

app.conf.broker_url = redis.from_url(os.environ['REDIS_URL'])
app.conf.result_backend = redis.from_url(os.environ['REDIS_URL'])

print(app.conf.broker_url)
print(app.conf.result_backend)


app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS, force=True)