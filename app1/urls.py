from django.contrib import admin
from django.urls import path, re_path
from app1 import views

app_name = 'app1'

urlpatterns = [
    re_path(r'^app1/$', views.register, name='app1'),
]
