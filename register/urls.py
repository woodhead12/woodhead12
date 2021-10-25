from django.contrib import admin
from django.urls import path, re_path
from register import views

urlpatterns = [
    re_path(r'^register/$', views.register),
]
