from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from web import models
from web.forms.project import ProjectModelForm


def project_list(request):
    form = ProjectModelForm()

    if request.method == 'POST':
        print(request.POST)
        form = ProjectModelForm(request=request, data=request.POST)

        if form.is_valid():
            form.instance.creator = request.usr
            form.save()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error': form.errors})

    return render(request, 'project_list.html', {'form': form})

