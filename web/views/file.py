from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web import models
from web.forms.file import FileUploadModelForm, FilePostModelForm
from utils.tencent.cos import delete_from_bucket, credential
import json
from django.conf import settings


def file(request, project_id):
    parent_obj = None
    menu_list = []
    folder_id = request.GET.get('folder_id', "")

    # 判断url中folder_id的参数格式
    if folder_id.isdigit():
        parent_obj = models.FileUpdate.objects.filter(file_type=2, project_id=project_id, id=folder_id).first()

        # 显示文件导航条
        row = parent_obj
        while row:
            menu_list.insert(0, {'id': row.id, 'name': row.name})
            row = row.parent

    # 显示文件列表 根据文件类型倒序排列
    if request.method == 'GET':
        form = FileUploadModelForm()
        if folder_id == '':
            file_list = models.FileUpdate.objects.filter(project_id=project_id, parent__isnull=True).order_by('-file_type')
        else:
            file_list = models.FileUpdate.objects.filter(project_id=project_id, parent_id=folder_id).order_by('-file_type')

        # 前端上传文件需要获取当前访问的目录 即父级目录 则返回一个parent_obj
        return render(request, 'manage/file.html', {'form': form, 'file_list': file_list, 'menu_list': menu_list, 'parent_obj': parent_obj})

    # 后端接收前端ajax提交的编辑文件夹数据 如果有fid 说明是编辑操作 如果没有fid 说明是创建操作
    edit_folder = None
    fid = request.POST.get('fid', '')
    print(request.POST)
    if fid.isdigit():
        edit_folder = models.FileUpdate.objects.filter(id=fid).first()

    # 表单中传入父级目录对象 方便创建文件夹对文件夹名进行校验
    form = FileUploadModelForm(request=request, parent_obj=parent_obj, data=request.POST, instance=edit_folder)
    if form.is_valid():
        form.instance.file_type = 2
        form.instance.project_id = project_id
        form.instance.parent = parent_obj
        form.instance.update_user = request.usr
        form.save()

        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


def file_delete(request, project_id):
    """
    删除文件
    """
    fid = request.GET.get('fid', "")
    print(fid)
    if not fid.isdigit():
        return
    delete_object = models.FileUpdate.objects.filter(id=fid, project_id=project_id).first()

    if delete_object.file_type == 2:
        # 找出被删除文件夹下的所有文件和文件夹
        keys = delete_folder_file(delete_object)
        objects = {
            'Quiet': 'true',
            'Object': keys
        }
        delete_from_bucket(request.project.bucket, objects=objects)

        # TODO: 删除文件后归还空间
        return JsonResponse({'status': True})

    else:
        # 如果删除的是文件 则直接删除即可
        delete_from_bucket(request.project.bucket, file_key=delete_object.key)
        delete_object.delete()
        return JsonResponse({'status': True})


def delete_folder_file(del_obj):
    """
    递归删除文件夹函数
    """
    child_keys = []

    if del_obj.file_type == 2:
        # 找出被删除文件夹下的所有文件和文件夹
        child_list = del_obj.child.all().order_by('-file_type')
        for child in child_list:
            # 如果文件夹下还存在文件夹 则递归执行函数
            if child.file_type == 2:
                delete_folder_file(child)
            else:
                child_keys.append({'Key': child.name})
                child.delete()

    return child_keys


@csrf_exempt
def cos(request, project_id):
    file_list = json.loads(request.body.decode('utf-8'))

    total_size = 0
    for f in file_list:
        total_size += f['size']
        # 单个文件大小限制  file_limit以M为单位
        file_limit_bytes = request.service.file_limit * 1024 * 1024
        if f['size'] > file_limit_bytes:
            return JsonResponse({'msg': "单个文件{}M大小上限, 上传文件{}达到上限!".format(request.service.file_limit, f['name'])})

    # 计算当前项目的剩余空间
    extra_space = request.service.space * 1024 * 1024 - request.project.used_space
    if total_size > extra_space:
        return JsonResponse({'msg': '当前项目上传文件容量达到上限!'})

    # 调用获取临时凭证方法
    result_dict = credential(request.project.bucket, request.project.region)
    return JsonResponse(result_dict)


@csrf_exempt
def file_post(request, project_id):
    print(request.POST)
    form = FilePostModelForm(data=request.POST)
    if form.is_valid():
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict['file_type'] = 1
        data_dict['project_id'] = project_id
        data_dict['update_user'] = request.usr
        instance = models.FileUpdate.objects.create(**data_dict)

        result = {
            'id': instance.id,
            'file_name': instance.name,
            'file_type': instance.get_file_type_display(),
            'file_size': instance.file_size,
            'update_usr': instance.update_user.usr,
            'update_datetime': instance.update_datetime,
        }

        return JsonResponse({'status': True, 'result': result})
    return JsonResponse({'status': True})
