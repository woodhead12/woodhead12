from django.contrib import admin
from django.urls import path, include, re_path
from web.views import account, project, manage, wiki, file, setting, issues


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
    re_path(r'^manage/(?P<project_id>\d+)/', include([
        re_path(r'^dashboard/$', manage.dashboard, name='dashboard'),
        re_path(r'^statistics/$', manage.statistics, name='statistics'),

        # ======== 文件上传
        re_path(r'^file/$', file.file, name='file'),
        # ======== ajax文件删除
        re_path(r'^file/del/$', file.file_delete, name='file_del'),
        # ======== 上传文件到cos桶获取临时凭证
        re_path(r'^cos/credential/$', file.cos, name='cos'),
        # ======== 文件上传同步到后端
        re_path(r'^file/post/$', file.file_post, name='file_post'),
        # ======== 文件下载
        re_path(r'^file/download/(?P<download_id>\w+)$', file.file_download, name='file_download'),


        re_path(r'^wiki/$', wiki.wiki, name='wiki'),
        # ======== 添加wiki文件
        re_path(r'^wiki/add/$', wiki.wiki_add, name='wiki_add'),
        # ======== 获取项目下对应的wiki文件目录
        re_path(r'^wiki/menu/$', wiki.wiki_menu, name='wiki_menu'),
        # ======== 删除wiki文件
        re_path(r'^wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
        # ======== 编辑wiki文件
        re_path(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
        # ======== wiki中md上传文件
        re_path(r'^wiki/upload/$', wiki.wiki_upload, name='wiki_upload'),

        # ======== 配置相关操作
        re_path(r'^setting/$', setting.setting, name='setting'),
        # ======== 配置中删除项目
        re_path(r'^setting/delete/$', setting.setting_delete, name='setting_delete'),

        # ======== 问题展示
        re_path(r'^issues/$', issues.issues, name='issues'),

    ], None))
]