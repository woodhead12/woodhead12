from django.shortcuts import render, HttpResponse, redirect
from web.forms.issues import IssuesModelForm


def issues(request, project_id):
    form = IssuesModelForm()
    return render(request, 'manage/issues.html', {'form': form})