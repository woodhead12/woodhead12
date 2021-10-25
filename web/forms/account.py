import re
from django import forms
from web.models import RegisterUserInfo
from django.core.exceptions import ValidationError


def mobile_validate(value):
    mobile_re = re.compile(r'^(13[0-9]|15[0-9]|17[0-9])[0-9]{8}')
    if not mobile_re.match(value):
        return ValueError('手机号格式错误')
    else:
        return True


class RegisterUserModelForm(forms.ModelForm):
    code = forms.CharField(label='验证码')
    phone = forms.CharField(label='手机号', validators=[mobile_validate, ], )
    pwd = forms.CharField(label='密码', widget=forms.PasswordInput())
    re_pwd = forms.CharField(label='重复密码', widget=forms.PasswordInput())

    class Meta:
        model = RegisterUserInfo
        fields = ['usr', 'email', 'pwd', 're_pwd', 'phone', 'code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)

    def clean_phone(self):
        val = self.cleaned_data.get('phone')
        if mobile_validate(val):
            return val
        else:
            raise ValidationError("手机格式错误")

    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('pwd')
        if pwd and re_pwd:
            if pwd == re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError('两次输入密码不一致')
        else:
            return self.cleaned_data
