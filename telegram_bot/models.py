from django.db import models
from django.contrib.auth.models import User
from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule

# Create your models here.

class Series(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    group_id = models.CharField(max_length=100)
    api_key = models.CharField(max_length=200)
    start_date = models.DateField(auto_now_add=True)
    no_of_post = models.IntegerField(default=0, null=True, blank=True)
    is_sent = models.BooleanField(default=False, null=True, blank=True)
    to_repeat = models.CharField(max_length=100, null=True, blank=True)
    cron_tab = models.ForeignKey(CrontabSchedule, null=True, blank=True, on_delete=models.SET_NULL)
    interval = models.ForeignKey(IntervalSchedule, null=True, blank=True, on_delete=models.SET_NULL)
    periodic_task = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.title}"

    @property
    def get_posts(self):
        return Post.objects.filter(series=self)

class Post(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True)
    is_sent = models.BooleanField(default=False, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} | {self.series.title}"