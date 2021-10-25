from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from web.forms.account import RegisterUserModelForm, CodeCheckForm \
    , SmsLoginForm


# 注册
def reg(request):
    form = RegisterUserModelForm()
    if request.method == 'POST':
        form = RegisterUserModelForm(data=request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error': form.errors})

    return render(request, 'register.html', {'form': form})


# 验证码发送 入缓存
def send_code(request):
    print('GET:', request.GET)
    form = CodeCheckForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


# 短信登录
def sms_login(request):
    form = SmsLoginForm()
    return render(request, 'login.html', {'form': form})
