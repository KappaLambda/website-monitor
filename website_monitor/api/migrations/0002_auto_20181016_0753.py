# Generated by Django 2.1.2 on 2018-10-16 07:53

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checktask',
            name='check_task_uuid',
        ),
        migrations.AddField(
            model_name='checktask',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='UUID'),
        ),
    ]
