from rest_framework import viewsets
from rest_framework.response import Response 
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from rest_framework.authtoken.models import Token
from django.utils import timezone
import json
import requests

from telegram_bot.models import Post, Series
from telegram_bot.serializers import *

PERIOD_CHOICES = {
    "daily":{"hour": 12},
    "wednesdays":{"day_of_week":3},
    "saturdays":{"day_of_week":6},
    "mon_to_fri":{"day_of_week":["mon","tue","wed","thur","fri","sat"]},
}

def create_periodic_schedule(periodic_schedule, series):
        
    if periodic_schedule == "daily" or periodic_schedule == {}:
        cron_tab = CrontabSchedule.objects.create(hour=12)
        series.to_repeat = "Every_day"

    elif periodic_schedule == "wednesday":
        cron_tab = CrontabSchedule.objects.create(day_of_week=3, hour=12)
        series.to_repeat = "Every Wednesdays"

    elif periodic_schedule == "saturdays":
        cron_tab = CrontabSchedule.objects.create(day_of_week=6, hour=12)
        series.to_repeat = "Every Weekends"

    elif periodic_schedule == "mon_to_fri":
        cron_tab = CrontabSchedule.objects.create(day_of_week=["mon","tue","wed","thur","fri"], hour=12)
        series.to_repeat = "Every Weekdays"

    return cron_tab

def create_inteval(interval, series):
    every = interval["every"]
    period = interval["period"]
    interval = IntervalSchedule.objects.create(every=every, period=period)
    series.to_repeat = f"Every {every} {period}"

    return interval


class SeriesViewSet(viewsets.ModelViewSet):
    
    serializer_class = SeriesInfoSerialier
    queryset = Series.objects.all()
    permission_classes =  (IsAuthenticated,)

    def list(self, request):
        author = request.user
        series_instances = Series.objects.filter(author = author)
        
        serialized_data = SeriesInfoSerialier(series_instances, many=True).data
        return Response(serialized_data)

    def retrieve(self, request, pk):
        series_instance = Series.objects.get(pk=pk)
        serialized_data = SeriesSerializer(series_instance).data
        return Response(serialized_data)    
    
    def create(self, request):
        title = request.data["title"]
        group_id = request.data["group_id"]
        api_key = request.data["api_key"]
        posts = request.data.get("posts")
        author = request.user     
        interval = request.data.get("interval")
        periodic_schedule = request.data.get("periodic_schedule")
        print(periodic_schedule)

        series = Series.objects.create(title=title, author=author, 
                                       group_id=group_id, api_key=api_key)

        if PeriodicTask.objects.filter(name=title).exists():
            return Response({"err":"This Name is Already taken"}, status=403)

        post_count = 0
        for post in posts:
            post_title = post["title"]
            content = post["content"]

            post = Post.objects.create(title=post_title, 
                                       content=content,
                                       series=series)
            post_count += 1

        if len(interval) != 0:
            print(interval)
            interval = create_inteval(interval, series)
            periodic_task = self.create_periodic_task(title, series, interval=interval)
            
        elif periodic_schedule is not None:
            cron_tab = create_periodic_schedule(periodic_schedule, series)          
            periodic_task = self.create_periodic_task(title, series, cron_tab=cron_tab)

        series.periodic_task = periodic_task
        series.no_of_post = post_count
        series.save()

        serialized_data = SeriesSerializer(series).data
        return Response(serialized_data)

    def create_periodic_task(self, title, series, interval=None, cron_tab=None):
        series_pk = series.pk
        app_dict = {"series":str(series_pk)}
        app_json = json.dumps(app_dict)
        periodic_task = PeriodicTask.objects.create(name=title, 
                                                    task="telegram_bot.tasks.send_message",
                                                    interval=interval, 
                                                    crontab = cron_tab,
                                                    enabled=True,
                                                    kwargs=app_json)
        return periodic_task
    
    def partial_update(self, request, pk):
        
        author = request.user
        series = request.data.get("series")
        periodic_task = request.data.get("periodic_task")
        periodic_schedule = request.data.get("periodic_schedule")
        interval = request.data.get("interval")
        series_instance = Series.objects.get(pk=pk)
            
        if author != series_instance.author:
            return Response({"err":"Your Not Authorized to Perform this Action"})        

        if series is not None:
            serializer = SeriesInfoSerialier(series_instance, request.data["series"], partial=True)
            if serializer.is_valid():
                serializer.save()
            
        elif periodic_task is not None:
            periodic_task_instance = series_instance.periodic_task
            
            periodic_task_instance.enabled = request.data["periodic_task"]
            periodic_task_instance.save()
            series_instance.is_sent = not series_instance.is_sent

        elif periodic_schedule is not None:            
            cron_tab_instance = series_instance.periodic_task.crontab 
            
            if cron_tab_instance is None:
                cron_tab = create_periodic_schedule(periodic_schedule, series_instance)       
                interval_to_delete = series_instance.periodic_task.interval

                series_instance.periodic_task.interval = None
                series_instance.periodic_task.crontab = cron_tab   
                series_instance.periodic_task.save()  

                interval_to_delete.delete()    
            
            else:         
                crontab_to_delete = series_instance.periodic_task.crontab

                cron_tab = create_periodic_schedule(periodic_schedule, series_instance)
                series_instance.periodic_task.crontab = cron_tab   
                series_instance.periodic_task.save()         

                crontab_to_delete.delete()

        elif interval is not None:
            interval_instance = series_instance.periodic_task.interval

            if interval_instance is None:
                interval_instance = create_inteval(interval, series_instance)
                interval_to_delete = series_instance.periodic_task.crontab
                
                series_instance.periodic_task.crontab = None
                series_instance.periodic_task.interval = interval_instance
                series_instance.periodic_task.save()

                interval_to_delete.delete()
            
            else:
                interval_to_delete = series_instance.periodic_task.interval

                interval = create_inteval(interval, series_instance)
                series_instance.periodic_task.interval = interval
                series_instance.periodic_task.save()

                interval_to_delete.delete()
        
        series_instance.save()
        serializer_data = SeriesSerializer(series_instance).data

        return Response(serializer_data)
            

class PostViewSet(viewsets.ModelViewSet):
    
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):        
        author = request.user
        series_id = request.GET.get("series_id")
        series_instances = Series.objects.filter(pk=series_id, author=author)
        
        if not series_instances.exists():    
            return Response({"err":"Your Not Authorized to perform this action"}, status=403)
        
        series = series_instances.first()
        post_instances = Post.objects.filter(series=series)
        
        serialized_data = PostSerializer(post_instances, many=True).data

        return Response(serialized_data) 

    def create(self, request):
        post = request.data["post"]
        series_id = post["series_id"]
        title = post["title"]
        content = post["content"]

        series_instance = Series.objects.get(pk=series_id)
        post_instance = Post.objects.create(title=title,
                                            content=content, 
                                            series=series_instance)
        series_instance.no_of_post += 1
        series_instance.is_sent = False
        series_instance.save()

        serialized_data = PostSerializer(post_instance).data
        return Response(serialized_data)

    def partial_update(self, request, pk):
        post = Post.objects.get(pk=pk)
        serializer = PostSerializer(post, request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk):
        user = request.user
        print(request.data)
        series_id = request.GET.get("series_id")
        print(series_id)
        series_instance = Series.objects.get(pk=series_id)
        series_instance.no_of_post -= 1
        series_instance.save()

        if series_instance.author == user:
            post = Post.objects.get(pk=pk)
            post.delete()

            return Response({"message":"Post deleted successfully"})

        return Response({"err":"Your Not Authorized To Perform this action"}, status=401)


        
class SignupViewSet(viewsets.ViewSet):
    
    def create(self, request):
        username = request.data["username"]
        password = request.data["password"]
        email = request.data["password"]

        user = User.objects.create_user(username=username, email=email, password=password)
        
        token = Token.objects.create(user=user)
        return Response({"token":token.key})
        
class CustomMessageViewSet(viewsets.ViewSet):

    def create(self, request):
        title = request.data["title"]
        content = request.data["content"]
        chat_id = request.data["chat_id"]
        api_key = request.data["api_key"]
        # api_key = "981855943:AAHElrIJ01s9MeL_3w1vBAmgCAkb2DpFl2A"

        content = content.replace("</p><p>", "\n")
        content = content.replace("<p>", "")
        content = content.replace("</p>", "\n")
        content = content.replace("<br>", "\n")

        print(content)
        url = f"https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={content}&parse_mode=html"
        data = requests.get(url)
        print(data.text)

        return Response({"message":"Message Sent"})