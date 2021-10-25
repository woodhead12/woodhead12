from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from web.forms.account import RegisterUserModelForm, CodeCheckForm


# 注册
def reg(request):
    form = RegisterUserModelForm()
    return render(request, 'register.html', {'form': form})


# 验证码发送 入缓存
def send_code(request):
    print('GET:', request.GET)
    form = CodeCheckForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})
