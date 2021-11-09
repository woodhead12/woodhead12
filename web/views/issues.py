import json
import uuid
import hashlib
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm, IssueInviteModelForm
from web import models
from utils.pagination import Pagination


class CheckFilter(object):
    def __init__(self, filter_list, request, name):
        self.request = request
        self.filter_list = filter_list
        self.name = name

    def __iter__(self):
        for ft in self.filter_list:
            ck = ""
            # 获取当前请求中status的相关参数
            param_list = self.request.GET.getlist(self.name)
            print(param_list)
            if str(ft[0]) in param_list:
                # 如果筛选条件在请求的参数值列表中 就给checkbox添加checked样式
                ck = "checked"
                param_list.remove(str(ft[0]))
            else:
                param_list.append(str(ft[0]))

            # 如果请求的url中存在page的分页参数 则渲染筛选条件确认框中的href要删除这个参数
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, param_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            if query_dict:
                url = "{}?{}".format(self.request.path_info, query_dict.urlencode())
            else:
                url = self.request.path_info

            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck}><label>{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=ft[1])
            yield mark_safe(html)


class SelectFilter(object):
    def __init__(self, filter_list, request, name):
        self.request = request
        self.filter_list = filter_list
        self.name = name

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;' >")
        # {'id': .., 'title': ...}
        for ft in self.filter_list:
            selected = ""
            fk_id = str(ft[0])
            fk_text = ft[1]
            param_list = self.request.GET.getlist(self.name)

            # 如果url中参数 过滤列表中有 添加selected属性
            if fk_id in param_list:
                selected = 'selected'
                param_list.remove(fk_id)
            else:
                param_list.append(fk_id)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, param_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected, text=fk_text)
            yield mark_safe(html)
        yield mark_safe("</select>")


def issues(request, project_id):
    form = IssuesModelForm(request)

    # 从url中获取筛选条件
    allow_filter_name = ['status', 'priority', 'issues_type']
    condition = {}
    for ft in allow_filter_name:
        ft_list = request.GET.getlist(ft)
        if not ft_list:
            continue

        # 拼接成ORM的筛选条件
        condition["{}__in".format(ft)] = ft_list

    print(condition)

    queryset = models.Issues.objects.filter(project_id=project_id, **condition)
    if request.method == 'GET':
        # 项目邀请表单
        invite_form = IssueInviteModelForm()

        # 对数据进行分页显示
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET
        )
        issues_object_list = queryset[page_object.start:page_object.end]

        # 获取当前项目的创建者以及参与者
        project_member = [(request.project.creator_id, request.project.creator.usr)]
        project_joiner = models.InProjectDetail.objects.filter(project_id=request.project.id).values_list('usr_id', 'usr__usr')
        project_member.extend(project_joiner)

        # 获取所有的问题类型
        issues_type = models.IssuesType.objects.filter(project_id=request.project.id).values_list('id', 'title')

        context = {
            'invite_form': invite_form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            # 将筛选条件渲染到页面上
            "filter_list": [
                {'title': '问题类型', 'filter': CheckFilter(issues_type, request, 'issues_type')},
                {'title': '状态', 'filter': CheckFilter(models.Issues.status_choices, request, 'status')},
                {'title': '优先级', 'filter': CheckFilter(models.Issues.priority_choices, request, 'priority')},
                {'title': '指派者', 'filter': SelectFilter(project_member, request, 'assign')},
                {'title': '关注者', 'filter': SelectFilter(project_member, request, 'attention')},
            ]

        }
        return render(request, 'manage/issues.html', context)

    # 接收前端的关于问题的ajax表单请求
    if request.method == 'POST':
        form = IssuesModelForm(request, data=request.POST)
        if form.is_valid():
            form.instance.creator = request.usr
            form.instance.project = request.project
            form.save()
            return JsonResponse({'status': True})
        return JsonResponse({'status': True, 'error': form.errors})

    return render(request, 'manage/issues.html', {'form': form})


def issues_detail(request, project_id, detail_id):
    # 问题编辑页面 返回有值的表单
    issue = models.Issues.objects.filter(id=detail_id, project_id=project_id).first()
    form = IssuesModelForm(request, instance=issue)

    return render(request, 'manage/issues_detail.html', {'form': form, 'issue': issue})


@csrf_exempt
def issues_record(request, project_id, record_id):
    if request.method == 'GET':
        # 这里的record_id 就是 issue的id号 即问题的id
        queryset = models.IssuesReply.objects.filter(issues_id=record_id, issues__project_id=project_id)

        # 因为返回的数据是queryset 要想前端能够接收到 就要构建python数据结构 然后json序列化
        data_list = []
        for row in queryset:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.usr,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)

        return JsonResponse({'status': True, 'data': data_list})

    # 接收前端 bindSubmit 方法的ajax请求提交的数据 然后存入数据库中
    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = record_id
        form.instance.reply_type = 2
        form.instance.creator = request.usr
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.usr,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }

        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})


def issues_change(request, project_id, change_id):
    issue_object = models.Issues.objects.filter(id=change_id, project_id=project_id).first()
    print(issue_object)

    def create_issue_reply(msg):
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            content=msg,
            issues=issue_object,
            creator=request.usr,
        )

        new_reply_dict = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.usr,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id
        }
        return new_reply_dict

    # 获取前端传递过来的变动的表单内容
    if request.method == 'POST':

        change_data = json.loads(request.body.decode('utf-8'))
        # 父问题和关注者在选择的时候会多传一次不携带name的change

        print(change_data)
        change_field_name = change_data['name']
        change_field_value = change_data['value']

        # 获取字段在模型中的字段对象
        field_obj = models.Issues._meta.get_field(change_field_name)

        # 文本类型字段处理
        if change_field_name in ['subject', 'desc', 'start_date', 'end_date']:
            if not change_field_value:
                # 如果更新的值为空 那么就要判断当前字段是否允许为空
                # 允许则为空 不允许则返回错误信息
                if field_obj.null:
                    setattr(issue_object, change_field_name, '')

                    # 生成修改问题记录
                    content = " {} 更新为空".format(field_obj.verbose_name)

                    issue_object.save()
                else:
                    return JsonResponse({'status': False, 'error': '当前字段的值不能为空'})
            else:
                setattr(issue_object, change_field_name, change_field_value)
                content = " {} 更新为 {}".format(field_obj.verbose_name, change_field_value)

                issue_object.save()

            return JsonResponse({'status': True, 'data': create_issue_reply(content)})

        # 外键类型字段处理
        if change_field_name in ['issues_type', 'module', 'parent', 'assign']:
            if not change_field_value:
                if field_obj.null:
                    setattr(issue_object, change_field_name, None)
                    issue_object.save()
                    content = " {} 更新为空".format(field_obj.verbose_name)
                else:
                    return JsonResponse({'status': False, 'error': '选择的值不能为空'})

            else:
                if change_field_name == 'assign':
                    # 判断指派的是否是项目创建者
                    if int(change_field_value) == request.project.creator_id:
                        instance = request.project.creator
                    # 不是项目创建者 则判断是否是项目参与者
                    else:
                        project_usr = models.InProjectDetail.objects.filter(project_id=project_id,
                                                                            usr_id=int(change_field_value)).first()
                        # 如果项目参与者存在 则获取参与者对应的用户对象
                        if project_usr:
                            instance = project_usr.usr
                        else:
                            instance = None

                    if not instance:
                        return JsonResponse({'status': False, 'error': '当前选择对象不存在'})

                    setattr(issue_object, change_field_name, instance)
                    issue_object.save()
                    content = " {} 更新为 {}".format(field_obj.verbose_name, str(instance))

                else:
                    # 获取外键字段关联的模型 并获取对象
                    instance = field_obj.remote_field.model.objects.filter(id=int(change_field_value),
                                                                           project_id=project_id).first()
                    if not instance:
                        return JsonResponse({'status': False, 'data': '您选择的值不存在'})

                    setattr(issue_object, change_field_name, instance)
                    issue_object.save()
                    content = " {} 更新为 {}".format(field_obj.verbose_name, str(instance))

            return JsonResponse({'status': True, 'data': create_issue_reply(content)})

        # 选择类型字段处理
        if change_field_name in ['priority', 'status', 'mode']:
            select_text = None
            for key, text in field_obj.choices:
                if str(key) == change_field_value:
                    select_text = text

            if not select_text:
                return JsonResponse({'status': False, 'error': '值不在选项中'})

            setattr(issue_object, change_field_name, change_field_value)
            issue_object.save()
            content = " {} 更新为 {}".format(field_obj.verbose_name, select_text)
            return JsonResponse({'status': True, 'data': create_issue_reply(content)})

        # 多对多字段处理
        if change_field_name == "attention":
            # {"name":"attention","value":[1,2,3]}
            if not isinstance(change_field_value, list):
                return JsonResponse({'status': False, 'error': "数据格式错误"})

            if not change_field_value:
                # 如果多对多字段变更的值为空 保存空值
                issue_object.attention.set(change_field_value)
                issue_object.save()
                content = "{}更新为空".format(field_obj.verbose_name)
            else:
                # values=[1,2,3,4]  ->   id是否是项目成员（参与者、创建者）
                # 创建者
                user_dict = {str(request.project.creator_id): request.project.creator.usr}
                # 参与者
                project_user_list = models.InProjectDetail.objects.filter(project_id=project_id)
                for item in project_user_list:
                    user_dict[str(item.usr_id)] = item.usr.usr

                username_list = []
                for user_id in change_field_value:
                    username = user_dict.get(str(user_id))
                    if not username:
                        return JsonResponse({'status': False, 'error': "用户不存在请重新设置"})
                    username_list.append(username)

                # 问题对象的多对多字段设置关系
                issue_object.attention.set(change_field_value)
                issue_object.save()
                content = "{}更新为{}".format(field_obj.verbose_name, ",".join(username_list))

            return JsonResponse({'status': True, 'data': create_issue_reply(content)})

        return JsonResponse({'status': False, 'error': "滚"})


@csrf_exempt
def invite_url(request, project_id):
    form = IssueInviteModelForm(data=request.POST)

    if form.is_valid():
        # 创建随机的邀请码 并保存到数据库中
        if request.usr == request.project.creator:
            # 当前登录的用户如果是项目创建者 则不用再被邀请
            pass
        else:
            form.add_error('period', '无权限创建邀请码')
            return JsonResponse({'status': False, 'error': form.errors})

        random_invite_code = "mdtukdmaskqwui"

        form.instance.project = request.project
        form.instance.code = random_invite_code
        form.instance.creator = request.usr

        form.save()

        url_to_html = 'http://' + request.get_host() + reverse('invite_join', kwargs={'code': random_invite_code})

        return JsonResponse({'status': True, 'data': url_to_html})


def invite_join(request, code):
    # 访问邀请码
    code_obj = models.ProjectInvite.objects.filter(code=code).first()

    if not code_obj:
        return HttpResponse("当前邀请码不存在")

    # 如果当前用户和邀请码的创建者是同一人
    if code_obj.project.creator == request.usr:
        return HttpResponse("创建者不需要重新加入")

    # 如果当前用户已经是当前项目的参与者 则不用加入
    member_join = models.InProjectDetail.objects.filter(project=code.project, urs=request.usr).exists()
    if member_join:
        return HttpResponse("已经是参与者 不用重复加入")

    # 从当前用户的价格策略获取成员限制
    member_limit = request.service.member
    current_num = models.InProjectDetail.objects.filter(project=code.project, urs=request.usr).count()

    if current_num > member_limit:
        return HttpResponse("项目成员超出上限")

    # 如果邀请限制数量少于已经邀请数量 则无法继续邀请
    if code_obj.count:
        if code_obj.use_count < code_obj.count:
            code_obj.use_count += 1
            code_obj.save()
        else:
            return HttpResponse("邀请数量超过上限")
    else:
        # 如果没有数量限制 则将当前用户添加到项目参与者中
        models.InProjectDetail.objects.create(usr=request.usr, project=code_obj.project)