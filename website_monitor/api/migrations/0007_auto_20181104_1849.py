# Generated by Django 2.1.2 on 2018-11-04 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20181104_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checktaskjob',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='checktask',
            unique_together=set(),
        ),
    ]
