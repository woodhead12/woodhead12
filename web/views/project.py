import time
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from web import models
from web.forms.project import ProjectModelForm
from utils.tencent.cos import create_bucket
from django.conf import settings


def project_list(request):
    form = ProjectModelForm()

    if request.method == 'POST':
        print(request.POST)
        form = ProjectModelForm(request=request, data=request.POST)

        if form.is_valid():
            # 在创建项目前创建桶
            project_name = form.cleaned_data['name']
            bucket_name = '{}-{}-{}-1300119432'.format(project_name, request.usr.phone, str(int(time.time())))

            create_bucket(bucket_name)

            form.instance.bucket = bucket_name
            form.instance.region = settings.COS_REGION

            form.instance.creator = request.usr

            # 创建项目的同时给项目即将创建的问题创建问题类型
            issue_types = ['功能', 'bug', '其他']
            issue_obj = []
            for issue_type in issue_types:
                issue_obj.append(models.IssuesType(project=form.instance, title=issue_type))

            models.IssuesType.objects.bulk_create(issue_obj)

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
    if project_type == 'join':
        models.InProjectDetail.objects.filter(project_id=project_id, usr=request.usr).update(star=True)
        return redirect('project_list')

    if project_type == 'my_project':
        models.ProjectDetail.objects.filter(id=project_id, creator=request.usr).update(star=False)
        return redirect('project_list')
    if project_type == 'join_project':
        models.InProjectDetail.objects.filter(project_id=project_id, usr=request.usr).update(star=False)
        return redirect('project_list')
