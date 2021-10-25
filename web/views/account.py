from django.shortcuts import render, HttpResponse
from web.forms.account import RegisterUserModelForm


def reg(request):
    form = RegisterUserModelForm()
    return render(request, 'register.html', {'form':form})
