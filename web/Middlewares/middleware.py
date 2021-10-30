import re
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import redirect
from web import models


class LoginMiddlewareMixin(MiddlewareMixin):
    def process_request(self, request):
        usr = request.session.get('user_id', 0)
        usr_obj = models.RegisterUserInfo.objects.filter(id=usr).first()

        request.usr = usr_obj

        # 如果单纯的没有从session获取到用户就跳转到登录页 那么即便跳转到登录页 因为没有登录 session中依旧没有值
        # 所以会出现死循环
        # 在配置文件中设置一个白名单 判断当前访问的url是否在白名单中 如果不在 则跳转到登录页面

        if request.path_info in settings.WITHOUT_AUTH_URL:
            return

        if not usr_obj:
            return redirect('login')

        # 登录成功后 获取当前用户的服务额度
        current_service = models.PayingRecord.objects.filter(usr=usr_obj).order_by('-id').first()

        # 将当前用户最新的服务的结束时间和当前时间进行比较
        current_end_time = current_service.end

        if not current_end_time or current_end_time < datetime.now():
            # 付费服务时间过期 则选择默认的服务额度
            default_service = models.ProjectManageService.objects.filter(id=1).first()
        else:
            default_service = models.ProjectManageService.objects.filter(id=current_service.service_id).first()

        request.service = default_service

    def process_view(self, request, view, args, kwargs):
        # 判断当前请求url是否是manage开头 如果是则渲染对应的功能菜单
        if not request.path_info.startswith('/manage/'):
            return

        # 如果从url参数中获取的project_id 是当前用户自己创建/自己参与的 则给request中添加一个项目参数
        project_id = kwargs.get('project_id')
        my_project = models.ProjectDetail.objects.filter(id=project_id, creator=request.usr).first()
        if my_project:
            request.project = my_project
            return

        join_project = models.InProjectDetail.objects.filter(project_id=project_id, usr=request.usr).first()
        if join_project:
            request.project = join_project
            return

        redirect('project_list')

