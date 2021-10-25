from django.contrib import admin
from django.urls import path, include, re_path
from web.views import register


urlpatterns = [
    re_path(r'^reg/$', register, name='reg')
]