from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from channel import views

urlpatterns = [
  url(r'^$',views.channel,name='channel'),
  url(r'^dashboard/+(?P<channel_id>\d+)/$$',views.dashboard,name='channel_dashboard'),
]