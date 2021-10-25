from django.shortcuts import render, HttpResponse
from django_redis import get_redis_connection
from register.forms import RegisterUserModelForm
from utils.tencent import sms


# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegisterUserModelForm(data=request.POST)
        if form.is_valid():
            return HttpResponse('注册成功')
        else:
            error = form.errors.get('__all__')
            return render(request, 'register/register.html', {'form': form, 'error': error})

    form = RegisterUserModelForm()
    return render(request, 'register/register.html', {'form': form})


def send_code(request):
    if request.method == 'POST':
        code = sms.return_register_code()
        phone = request.POST.get('phone')
        print(phone, code)
        # 再将验证码存入redis中
        conn = get_redis_connection('default')
        conn.set(phone, code, ex=60)

        return HttpResponse("OK!")
    return HttpResponse("OK!")

