# Generated by Django 2.0.2 on 2018-03-22 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0002_auto_20180322_2343'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel_sub',
            old_name='date',
            new_name='date1',
        ),
    ]