# Generated by Django 2.2.4 on 2019-09-01 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0004_series_api_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('content', models.TextField(blank=True, default=None, null=True)),
                ('sent_time', models.DateTimeField(auto_now=True)),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='telegram_bot.Series')),
            ],
        ),
    ]
