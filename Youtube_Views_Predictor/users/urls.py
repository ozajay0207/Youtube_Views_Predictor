from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from users import views

urlpatterns = [
    url(r'^$',views.DashBoard,name='DashBoard'),
    url(r'^Sign_Up/$',views.Sign_Up,name='Sign_Up'),
    url(r'^Sign_In/$',views.Sign_In,name='Sign_In'),
    url(r'^Sign_Out/$',views.Sign_Out,name='Sign_Out'),
    url(r'^login/$',views.login,name='Log_In'),
    url(r'^register/$',views.register,name='Register'),
    url(r'^validate_email/$',views.validate_email,name='vaidate_email'),
    url(r'^validate_display_name/$',views.validate_display_name,name='vaidate_display_name'),
    url(r'^get_data/$',views.get_data,name="get_data"),
    url(r'^dashboard/channel/+(?P<channel_id>\d+)/$',views.view_channel_dashboard,name="view_dashboard"),
    url(r'^dashboard/views_analysis/weekly/+(?P<video_id>\d+)/$',views.weekly_view_video_analysis,name="weekly_view_analysis"),
    url(r'^dashboard/views_analysis/bimonthly/+(?P<video_id>\d+)/$',views.bimoonthly_view_video_analysis,name="bimonthly_view_analysis"),
    url(r'^dashboard/views_analysis/monthly/+(?P<video_id>\d+)/$',views.monthly_view_video_analysis,name="monthly_view_analysis"),
    url(r'^dashboard/views_analysis/total/+(?P<video_id>\d+)/$',views.total_view_video_analysis,name="total_view_analysis"),


    #url(r'^get_data/$',views.get_data,name="get_data"),
]