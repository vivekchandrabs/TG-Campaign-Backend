# Generated by Django 2.2.4 on 2019-08-26 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0002_auto_20190824_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='series',
            name='group_id',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
    ]
