# Generated by Django 2.0.2 on 2018-04-01 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20180401_1622'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video_sub',
            old_name='date',
            new_name='date1',
        ),
    ]
