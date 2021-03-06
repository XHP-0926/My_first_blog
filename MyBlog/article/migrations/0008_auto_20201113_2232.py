# Generated by Django 3.1.2 on 2020-11-13 22:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0007_auto_20201113_1947'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepost',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='article/%Y%m%d/'),
        ),
        migrations.AlterField(
            model_name='articlepost',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 13, 22, 32, 9, 247053)),
        ),
    ]
