from django.db import models

# Create your models here.

class channel_main(models.Model):
    channel_name = models.TextField(unique=True)
    channel_category = models.CharField(max_length = 100,null=True)
    channel_url = models.CharField(max_length=1000,default='none',null=True)
    social_url = models.CharField(max_length=1000,default='none')
    channel_img_url = models.CharField(max_length=1000,default='none',null=True)

class channel_sub(models.Model):
    channel_id = models.ForeignKey(channel_main,on_delete=models.CASCADE)
    date1 = models.CharField(max_length=15)
    view_count=models.BigIntegerField(blank=False)
    subscriber_count = models.BigIntegerField(blank=False)

class video_data(models.Model):
    channel_id=models.ForeignKey(channel_main,on_delete=models.CASCADE)
    video_name=models.TextField()
    upload_date=models.TextField()
    video_url=models.TextField()
    comment_count=models.FloatField()
    view_count = models.FloatField()
