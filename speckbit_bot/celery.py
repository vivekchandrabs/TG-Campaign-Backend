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

app.conf.broker_url = "redis://h:pb65d80ca7193ffad8a487d340f9a3dc0c80ed0b33873df75edeed91cc705a4cf@ec2-3-213-249-196.compute-1.amazonaws.com:14739"
app.conf.result_backend = "redis://h:pb65d80ca7193ffad8a487d340f9a3dc0c80ed0b33873df75edeed91cc705a4cf@ec2-3-213-249-196.compute-1.amazonaws.com:14739"


app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS, force=True)