from __future__ import absolute_import

import django
import redis
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speckbit_bot.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

django.setup()

app = Celery('speckbit_bot')

app.conf.broker_url = os.environ.get("REDIS_URL", 'redis://localhost:6379/0')
app.conf.result_backend = os.environ.get("REDIS_URL", 'redis://localhost:6379/0')


app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS, force=True)