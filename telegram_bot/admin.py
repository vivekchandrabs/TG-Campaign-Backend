from django.contrib import admin
from telegram_bot.models import Post, Series, CustomMessage

# Register your models here.

admin.site.register(Post)
admin.site.register(Series)
admin.site.register(CustomMessage)