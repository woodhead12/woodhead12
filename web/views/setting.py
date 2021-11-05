from django.shortcuts import render, HttpResponse, redirect
from web import models
from utils.tencent.cos import delete_bucket


def setting(request, project_id):
    return render(request, 'manage/setting.html')


def setting_delete(request, project_id):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')

        delete_project = models.ProjectDetail.objects.filter(id=project_id, name=project_name).first()
        if delete_project:
            # 删除桶  同时考虑到创建桶时候的读写模式 私有 公有读私有写  私有情况下桶无法被删除
            delete_bucket(delete_project.bucket, delete_project.region)
            delete_project.delete()
            return redirect('project_list')

    return render(request, 'manage/setting_delete.html')

