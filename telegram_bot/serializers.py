from rest_framework import serializers
from django.contrib.auth.models import User
from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule

from telegram_bot.models import Post, Series

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ("id", "username", "email")


class PeriodicTaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PeriodicTask
        fields = ("id", "enabled")


class SeriesSerializer(serializers.ModelSerializer):
    
    posts = serializers.SerializerMethodField()
    author = UserSerializer()
    periodic_task = PeriodicTaskSerializer()

    def get_posts(self, obj):
        posts = obj.get_posts
        serialized_data = PostSerializer(posts, many=True).data 
        return serialized_data

    class Meta:
        model = Series
        fields = ("id", "title", "author", "start_date", "no_of_post", "is_sent", 
                    "to_repeat", "posts", "group_id", "periodic_task")
        depth = 1
        

class SeriesInfoSerialier(serializers.ModelSerializer):
    
    author = UserSerializer()

    class Meta:
        model = Series
        fields = ("id", "title", "author", "start_date", "no_of_post", "is_sent", "to_repeat", "group_id")
        

class PostSerializer(serializers.ModelSerializer):
    
    series = serializers.SerializerMethodField()

    def get_series(self, obj):
        series = {}
        series["id"] = obj.series.pk
        series["title"] = obj.series.title
        return series

    class Meta:
        model = Post
        fields = ("id", "series", "is_sent", "title", "content")


class IntervalScheduleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = IntervalSchedule
        fields = ("id", "every", "period")


class CrontabScheduleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CrontabSchedule
        fields = "__all__"