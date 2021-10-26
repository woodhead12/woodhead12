from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from web.forms.account import RegisterUserModelForm, CodeCheckForm \
    , SmsLoginForm, NormalLoginForm
from utils.pic_for_pillow.code_pic import check_code


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
    return render(request, 'sms_login.html', {'form': form})


# 手机号或者邮箱加密码登录
def normal_login(request):
    form = NormalLoginForm()
    if request.method == 'POST':

        form = NormalLoginForm(request=request, data=request.POST)
        if form.is_valid():
            # TODO: 将用户判断的逻辑放在视图中 不写在clean方法中

            request.session['user'] = form.cleaned_data.get('email_or_phone')
            return redirect('index')
        else:
            return render(request, 'login.html', {'form': form})

    return render(request, 'login.html', {'form': form})


# 获取图片验证码
def get_code(request):
    img, code = check_code()

    # 获取图片验证码后将code写入session中
    request.session['code'] = code
    request.session.set_expiry(60)

    print(code)
    from io import BytesIO
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


# 退出登录
def login_exit(request):
    request.session.flush()
    return redirect('index')