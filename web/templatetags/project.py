from django.shortcuts import reverse
from django.template import Library
from web import models

register = Library()


@register.inclusion_tag('inclusion/project_menu.html')
def show_all_projects(request):
    # 获取当前用户创建的项目
    my_projects = models.ProjectDetail.objects.filter(creator=request.usr)

    # 获取当前用户参与的项目
    join_projects = models.InProjectDetail.objects.filter(usr=request.usr)

    return {'my': my_projects, 'join': join_projects, 'request':request}


@register.inclusion_tag('inclusion/manage_menu.html')
def get_manage_menu(request):
    menu_list = [
        {'title': '概览', 'url': reverse('dashboard', kwargs={'project_id': request.project.id})},
        {'title': '问题', 'url': reverse('issues', kwargs={'project_id': request.project.id})},
        {'title': '统计', 'url': reverse('statistics', kwargs={'project_id': request.project.id})},
        {'title': '附件', 'url': reverse('file', kwargs={'project_id': request.project.id})},
        {'title': 'wiki', 'url': reverse('wiki', kwargs={'project_id': request.project.id})},
        {'title': '设置', 'url': reverse('setting', kwargs={'project_id': request.project.id})},
    ]

    for url_dict in menu_list:
        if request.path_info.startswith(url_dict['url']):
            url_dict['style'] = 'active'

    return {'menu_list': menu_list}
