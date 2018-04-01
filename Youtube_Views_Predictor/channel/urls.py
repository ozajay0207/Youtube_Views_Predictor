from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from channel import views

urlpatterns = [
  url(r'^$',views.channel,name='channel'),
  url(r'^dashboard/+(?P<channel_id>\d+)/$',views.dashboard,name='channel_dashboard'),
  url(r'^dashboard/views_analysis/total/+(?P<channel_id>\d+)/$',views.total_analysis,name='total_view_analysis'),
  url(r'^dashboard/views_analysis/monthly/+(?P<channel_id>\d+)/$',views.monthly_analysis,name='monthly_view_analysis'),
  url(r'^dashboard/views_analysis/bimonthly/+(?P<channel_id>\d+)/$',views.bimonthly_analysis,name='bimonthly_view_analysis'),
  url(r'^dashboard/views_analysis/weekly/+(?P<channel_id>\d+)/$',views.weekly_analysis,name='weekly_view_analysis'),
]