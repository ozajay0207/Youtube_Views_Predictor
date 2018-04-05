from django.db import models

# Create your models here.

class users(models.Model):
    Email = models.CharField(max_length = 100)
    Display_Name = models.CharField(max_length=50)
    Password=models.CharField(max_length = 100)
    def __str__(self):
        return self.Email

class video_main(models.Model):
    video_name = models.CharField(max_length=200)
    category=models.CharField(max_length=100)
    youtube_url=models.CharField(max_length=500)
    publish_date=models.CharField(max_length=30)
    analysis_status=models.BooleanField(default=False)
    user_id=models.ForeignKey(users,on_delete=models.CASCADE)
    def __str__(self):
        return self.video_name

class video_sub(models.Model):
    video_main_id=models.ForeignKey(video_main,on_delete=models.CASCADE)
    date1=models.CharField(max_length=100)
    view=models.BigIntegerField(default=0)
    likes=models.BigIntegerField(default=0)
    dislikes=models.BigIntegerField(default=0)
    def __str__(self):
        return self.video_main_id.video_name + ' ' + self.date1

class user_channel_main(models.Model):
    channel_name = models.CharField(max_length=100,unique=True)
    category = models.CharField(max_length=100)
    channel_url = models.CharField(max_length=500,default='none')
    channel_image_url = models.CharField(max_length=500,default='none')
    analysis_status=models.BooleanField(default=False)
    user_id=models.ForeignKey(users,on_delete=models.CASCADE)
    def __str__(self):
        return self.channel_name

class user_channel_sub(models.Model):
    channel_id = models.ForeignKey(user_channel_main,on_delete=models.CASCADE)
    date1 = models.CharField(max_length=100)
    view_count=models.BigIntegerField(blank=False)
    subscriber_count = models.BigIntegerField(blank=False)
    def __str__(self):
        return self.channel_id.channel_name

