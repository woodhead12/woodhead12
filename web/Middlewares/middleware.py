from django.utils.deprecation import MiddlewareMixin


class LoginMiddlewareMixin(MiddlewareMixin):
    def process_request(self, request):
        usr_obj = request.session.get('user')
        if usr_obj:
            request.flag = True
            request.user = usr_obj
        else:
            request.flag = False
