from django.db import models

# Create your models here.

class channel_main(models.Model):
    channel_name = models.CharField(max_length = 100,unique=True)
    category = models.CharField(max_length = 100)
    channel_url = models.CharField(max_length=1000,default='none')
    social_blade_url = models.CharField(max_length=1000,default='none')
    channel_image_url = models.CharField(max_length=1000,default='none')

class channel_sub(models.Model):
    channel_id = models.ForeignKey(channel_main,on_delete=models.CASCADE)
    date1 = models.CharField(max_length=15)
    view_count=models.BigIntegerField(blank=False)
    subscriber_count = models.BigIntegerField(blank=False)