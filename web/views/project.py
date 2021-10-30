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

    project_dict = {'star': [], 'my': [], 'join': []}

    # 显示项目列表 我创建的项目
    my_projects = models.ProjectDetail.objects.filter(creator=request.usr)
    join_projects = models.InProjectDetail.objects.filter(usr=request.usr)
    for project in my_projects:
        if project.star:
            project.class_type = 'my_project'
            project_dict['star'].append(project)
        else:
            project_dict['my'].append(project)

    for project in join_projects:
        if project.star:
            project.class_type = 'join_project'
            project_dict['star'].append(project)
        else:
            project_dict['join'].append(project)

    return render(request, 'project_list.html', {'form': form, 'project_dict': project_dict})


def project_star(request, project_type, project_id):
    """
    星标确认
    """
    if project_type == 'my':
        models.ProjectDetail.objects.filter(id=project_id, creator=request.usr).update(star=True)
        return redirect('project_list')
    elif project_type == 'join':
        models.InProjectDetail.objects.filter(project_id=project_id, usr=request.usr).update(star=True)
        return redirect('project_list')


def project_star_cancel(request, project_type, project_id):
    """
    星标取消
    """
    if project_type == 'my_project':
        models.ProjectDetail.objects.filter(id=project_id, creator=request.usr).update(star=False)
        return redirect('project_list')
    elif project_type == 'join_project':
        models.InProjectDetail.objects.filter(project_id=project_id, usr=request.usr).update(star=False)
        return redirect('project_list')