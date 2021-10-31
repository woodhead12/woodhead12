from django.shortcuts import render, HttpResponse, redirect


def dashboard(request, project_id):
    return render(request, 'manage/dashboard.html')


def issues(request, project_id):
    return render(request, 'manage/issues.html')


def statistics(request, project_id):
    return render(request, 'manage/statistics.html')


def file(request, project_id):
    return render(request, 'manage/file.html')


def setting(request, project_id):
    return render(request, 'manage/setting.html')
