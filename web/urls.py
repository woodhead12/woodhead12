from django.contrib import admin
from django.urls import path, include, re_path
from web.views import account


urlpatterns = [
    re_path(r'^reg/$', account.reg, name='reg')
]