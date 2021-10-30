from django.contrib import admin
from django.urls import path, re_path, include
from app1 import views

app_name = 'app1'

urlpatterns = [
    re_path(r'^app1/$', views.register, name='app1'),
    re_path(r'^phone/$', views.send_code,),
    re_path(r'^create_project/$', views.create_project, name='cp')
]
