from django import forms
from django.core.exceptions import ValidationError
from .account import WidgetAttrsForm

from web import models


class ProjectModelForm(WidgetAttrsForm, forms.ModelForm):
    class Meta:
        model = models.ProjectDetail
        fields = ['name', 'color', 'desc']

        widgets = {
            'desc': forms.Textarea(attrs={'cols': '40', 'rows': '20'})
        }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data.get('name')
        print(name)
        exists = models.ProjectDetail.objects.filter(name=name, creator=self.request.usr).exists()
        print(exists)

        count = models.ProjectDetail.objects.filter(creator=self.request.usr).count()
        if exists:
            raise ValidationError('当前项目已被创建!请重新命名!')

        print(count, self.request.service.count)

        if count >= self.request.service.count:
            raise ValidationError('当前创建项目数量达到上限!请进行付费扩充!')

        return name
