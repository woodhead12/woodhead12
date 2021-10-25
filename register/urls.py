from django.contrib import admin
from django.urls import path, re_path
from register import views

app_name = 'register'

urlpatterns = [
    re_path(r'^register/$', views.register, name='register'),
]
