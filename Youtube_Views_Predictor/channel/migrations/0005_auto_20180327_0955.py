# Generated by Django 2.0.2 on 2018-03-27 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0004_auto_20180323_1412'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel_main',
            old_name='channel_image_url',
            new_name='social_url',
        ),
        migrations.RemoveField(
            model_name='channel_main',
            name='category',
        ),
        migrations.RemoveField(
            model_name='channel_main',
            name='social_blade_url',
        ),
        migrations.AddField(
            model_name='channel_main',
            name='channel_category',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='channel_main',
            name='channel_img_url',
            field=models.CharField(default='none', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='channel_main',
            name='channel_name',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='channel_main',
            name='channel_url',
            field=models.CharField(default='none', max_length=1000, null=True),
        ),
    ]