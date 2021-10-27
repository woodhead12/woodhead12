from django.shortcuts import render, HttpResponse, redirect
from web import models


def project_list(request):
    return render(request, 'project_list.html')