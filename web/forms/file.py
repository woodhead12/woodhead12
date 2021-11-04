from django import forms
from django.core.exceptions import ValidationError
from .account import WidgetAttrsForm
from web import models


class FileUploadModelForm(WidgetAttrsForm, forms.ModelForm):
    class Meta:
        model = models.FileUpdate
        fields = ['name']

    def __init__(self, request=None, parent_obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_obj = parent_obj

    # 如果需要校验文件夹名称是否重复 则进行校验
    def clean_name(self):
        name = self.cleaned_data.get('name')
        # 如果当前创建的文件夹是在顶级目录 即没有父级目录
        queryset = models.FileUpdate.objects.filter(file_type=2, name=name, project=self.request.project,)
        if not self.parent_obj:
            folder = queryset.filter(parent__isnull=True).exists()
        else:
            folder = queryset.filter(parent=self.parent_obj).exists()

        if folder:
            raise ValidationError('当前项目下的文件夹名重复!')

        return name


class FilePostModelForm(WidgetAttrsForm, forms.ModelForm):
    etag = forms.CharField(label='etag')

    class Meta:
        model = models.FileUpdate
        exclude = ['file_type', 'project', 'update_datetime', 'update_user']

    # TODO: etag文件校验
