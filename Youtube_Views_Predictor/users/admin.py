from django.contrib import admin
from users.models import user_channel_main,user_channel_sub,users,video_main,video_sub

# Register your models here.
admin.site.register(users)
admin.site.register(video_main)
admin.site.register(video_sub)
admin.site.register(user_channel_main)
admin.site.register(user_channel_sub)
