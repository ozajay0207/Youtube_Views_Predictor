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
]