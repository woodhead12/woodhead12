from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from web import models
from web.forms.file import FileUploadModelForm


def file(request, project_id):
    parent_obj = None
    folder_id = request.GET.get('folder_id', "")

    # 如果url中的参数格式不正确 则跳转到文件显示界面
    if folder_id.isdigit():
        parent_obj = models.FileUpdate.objects.filter(file_type=2, project_id=project_id, id=folder_id).first()

    if request.method == 'GET':
        form = FileUploadModelForm()
        return render(request, 'manage/file.html', {'form': form})

    # 表单中传入父级目录对象 方便创建文件夹对文件夹名进行校验
    form = FileUploadModelForm(request=request, parent_obj=parent_obj, data=request.POST)
    if form.is_valid():
        form.instance.file_type = 2
        form.instance.project_id = project_id
        form.instance.parent = parent_obj
        form.instance.update_user = request.usr
        form.save()

        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


