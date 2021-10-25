from django.shortcuts import render, HttpResponse


def reg(request):
    return render(request, 'register.html')
