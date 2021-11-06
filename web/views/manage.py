from django.shortcuts import render, HttpResponse, redirect


def dashboard(request, project_id):
    return render(request, 'manage/dashboard.html')


def statistics(request, project_id):
    return render(request, 'manage/statistics.html')


