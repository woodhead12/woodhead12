from django import forms
from django.core.exceptions import ValidationError
from .account import WidgetAttrsForm
from web import models


class IssuesModelForm(WidgetAttrsForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            "assign": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "attention": forms.SelectMultiple(
                attrs={'class': "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
            "parent": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "start_date": forms.DateTimeInput(attrs={'autocomplete': "off"}),
            "end_date": forms.DateTimeInput(attrs={'autocomplete': "off"})
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        # 问题指派 必须是参与项目得人或者是创建项目的人
        total_usr = [(self.request.usr.id, self.request.usr.usr)]
        join_usr = models.InProjectDetail.objects.filter(project=self.request.project).values_list('usr_id', 'usr__usr')
        total_usr.extend(join_usr)
        self.fields['assign'].choices = total_usr
        # 问题关注者 同问题指派
        self.fields['attention'].choices = [('', '没有选择任何项')] + total_usr

        # 问题类型
        self.fields['issues_type'].choices = models.IssuesType.objects.filter(project=self.request.project).values_list('id', 'title')

        # 当前项目下的所有模块
        total_module = [('', '没有选择任何项')]
        project_module = models.Module.objects.filter(project=self.request.project).values_list('id', 'title')
        total_module.extend(project_module)
        self.fields['module'].choices = total_module

        # 父级问题 只能选择当前问题下的所有问题
        parent_issue = models.Issues.objects.filter(project=self.request.project).values_list('id', 'subject')
        whole_issue = [('', '没有选择任何项')]
        whole_issue.extend(parent_issue)
        self.fields['parent'].choices = whole_issue


class IssuesReplyModelForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']


class IssueInviteModelForm(WidgetAttrsForm, forms.ModelForm):
    class Meta:
        model = models.ProjectInvite
        fields = ['period', 'count']