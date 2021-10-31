from django import forms
from django.core.exceptions import ValidationError
from .account import WidgetAttrsForm

from web import models


class WikiModelForm(WidgetAttrsForm, forms.ModelForm):
    class Meta:
        model = models.WikiArticle
        # 将关联的项目字段排除 默认创建的时候填入当前url中project_id对应的项目
        exclude = ['project']

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        # 修改外键经过modelForm渲染出来的选择的值
        origin_list = [('', '请选择父wiki')]
        data_list = models.WikiArticle.objects.filter(project=self.request.project).values_list('id', 'title')
        origin_list.extend(data_list)
        self.fields['parent_wiki'].choices = origin_list
