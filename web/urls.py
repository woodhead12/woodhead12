from django.contrib import admin
from django.urls import path, include, re_path
from web.views import account, project, manage


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

    # ======== 星标项目确认和取消
    re_path(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),

    # ======== 项目下的功能模块
    re_path(r'^manage/(?P<project_id>\w+)/', include([
        re_path(r'^dashboard/$', manage.dashboard, name='dashboard'),
        re_path(r'^issues/$', manage.issues, name='issues'),
        re_path(r'^statistics/$', manage.statistics, name='statistics'),
        re_path(r'^file/$', manage.file, name='file'),
        re_path(r'^wiki/$', manage.wiki, name='wiki'),
        re_path(r'^setting/$', manage.setting, name='setting'),
    ], None))
]