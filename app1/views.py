import random
from datetime import datetime
from django.shortcuts import render, HttpResponse
from django_redis import get_redis_connection
from app1 import models
from app1.forms import RegisterUserModelForm, ProjectForm
from utils.tencent import sms


# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegisterUserModelForm(data=request.POST)
        if form.is_valid():
            instance = form.save()
            usr_id = instance.id
            service = models.ProjectManageService.objects.get(type='免费服务')

            models.PayingRecord.objects.create(type='已支付', real_pay=0, begin=datetime.now(),
                                               end=None, usr_id=usr_id, service=service)
            return HttpResponse('注册成功')
        else:
            error = form.errors.get('__all__')
            return render(request, 'register/register.html', {'form': form, 'error': error})

    form = RegisterUserModelForm()
    return render(request, 'register/register.html', {'form': form})


def send_code(request):
    if request.method == 'GET':
        phone = request.GET.get('phone')
        random_code = random.randrange(100000, 999999)
        print(random_code)
        code = sms.return_register_code(phone, random_code)

        print(phone, code)
        # 再将验证码存入redis中
        conn = get_redis_connection('default')
        conn.set(phone, code, ex=60)

        return HttpResponse("OK!")
    return HttpResponse("OK!")


def create_project(request):
    form = ProjectForm()

    if request.method == 'POST':
        print(request.POST)

        create_data = {
            'name': request.POST.get('name'),
            'desc': request.POST.get('desc'),
            'color': '#6c6c6c',
            'star': False,
            'member': 5,
            'used_space': 10,
            'creator_id': 2,
        }

        models.ProjectDetail.objects.create(**create_data)
        return HttpResponse("OK!")

    projects = models.ProjectDetail.objects.all()
    return render(request, 'project/project.html', {'form': form, 'projects': projects})
