from __future__ import absolute_import, unicode_literals
from celery import task
from speckbit_bot.celery import app
import requests

from telegram_bot.models import Post, Series

@app.task
def send_message(series):
    
    print("Beat is sending and the worker is receiving")
    series = Series.objects.get(pk=series)
    chat_id = series.group_id
    posts = Post.objects.filter(series=series, is_sent=False)
    print(posts)
    print(series.enabled)
    if posts.exists():
    	post = posts.first()
    	post.is_sent = True
    	post.save()

    	title = post.title
    	content = post.content

    	url = f"https://api.telegram.org/bot981855943:AAHElrIJ01s9MeL_3w1vBAmgCAkb2DpFl2A/sendMessage?chat_id={chat_id}&text={content}&parse_mode=Markdown"
    	data = requests.get(url)

    else:

    	series.is_sent = True
    	series.save()

    	series.periodic_task.enabled = False
    	series.periodic_task.save()












