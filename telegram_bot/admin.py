from django.contrib import admin
from telegram_bot.models import Post, Series

# Register your models here.

admin.site.register(Post)
admin.site.register(Series)