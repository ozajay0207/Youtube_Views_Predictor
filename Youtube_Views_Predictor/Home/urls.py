from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from Home import views

urlpatterns = [
  url(r'^$',views.Home,name='home'),

]