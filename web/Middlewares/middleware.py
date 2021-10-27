import re
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import redirect


class LoginMiddlewareMixin(MiddlewareMixin):
    def process_request(self, request):
        usr_obj = request.session.get('user')

        # 如果单纯的没有从session获取到用户就跳转到登录页 那么即便跳转到登录页 因为没有登录 session中依旧没有值
        # 所以会出现死循环
        # 在配置文件中设置一个白名单 判断当前访问的url是否在白名单中 如果不在 则跳转到登录页面

        # if request.path_info in settings.WITHOUT_AUTH_URL:
        #     if usr_obj:
        #         request.flag = True
        #         request.user = usr_obj
        #     else:
        #         request.flag = False
        # else:
        #     return redirect('login')

        # 登录成功后 获取当前用户的服务额度
