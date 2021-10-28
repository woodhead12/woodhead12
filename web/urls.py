from django.contrib import admin
from django.urls import path, include, re_path
from web.views import account, project


urlpatterns = [
    re_path(r'^phone/$', account.send_code, name='sms'),
    re_path(r'^reg/$', account.reg, name='reg'),
    re_path(r'^sms_login/$', account.sms_login, name='sms_login'),
    re_path(r'^login/$', account.normal_login, name='login'),

    re_path(r'^index/$', account.index, name='index'),

    # ======== 获取图片验证码
    re_path(r'^code/$', account.get_code, name='code'),

    # ======== 退出登录
    re_path(r'^exit/$', account.login_exit, name='exit'),

    # ======== 项目管理
    re_path(r'^project/list/$', project.project_list, name='project_list'),
]