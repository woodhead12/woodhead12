import re
import random
import hashlib
from django import forms
from web.models import RegisterUserInfo
from django_redis import get_redis_connection
from django.db.models import Q

from utils.tencent import sms
from django.core.exceptions import ValidationError


def mobile_validate(value):
    mobile_re = re.compile(r'^(13[0-9]|15[0-9]|17[0-9])[0-9]{8}')
    if not mobile_re.match(value):
        raise ValidationError("手机格式错误")
    else:
        return True


class WidgetAttrsForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)


class RegisterUserModelForm(WidgetAttrsForm, forms.ModelForm):
    code = forms.CharField(label='验证码', error_messages={'required': '当前字段必填!'})
    phone = forms.CharField(label='手机号', validators=[mobile_validate, ], error_messages={'required': '当前字段必填!'})
    pwd = forms.CharField(label='密码', widget=forms.PasswordInput(), error_messages={'required': '当前字段必填!'})
    re_pwd = forms.CharField(label='重复密码', widget=forms.PasswordInput(), error_messages={'required': '当前字段必填!'})

    class Meta:
        model = RegisterUserInfo
        fields = ['usr', 'email', 'pwd', 're_pwd', 'phone', 'code']

    def clean_usr(self):
        val = self.cleaned_data.get('usr')
        obj = RegisterUserInfo.objects.filter(usr=val).exists()
        if obj:
            raise ValidationError('当前用户名已被注册!')

        return val

    def clean_pwd(self):
        val = self.cleaned_data.get('pwd')
        encrypt_val = hashlib.md5(val.encode('utf-8')).hexdigest()

        return encrypt_val

    def clean_re_pwd(self):
        val = self.cleaned_data.get('re_pwd')
        encrypt_re_val = hashlib.md5(val.encode('utf-8')).hexdigest()

        if encrypt_re_val != self.cleaned_data.get('pwd'):
            raise ValidationError('两次输入的密码不一致!')

        return encrypt_re_val

    def clean_phone(self):
        val = self.cleaned_data.get('phone')
        if mobile_validate(val):
            return val
        else:
            self.add_error('phone', '输入手机号格式错误!')
            return val

    def clean_code(self):
        val = self.cleaned_data.get('code')
        phone = self.cleaned_data.get('phone')
        conn = get_redis_connection()
        redis_code = conn.get(phone).decode('utf-8')

        if val.strip() != redis_code:
            raise ValidationError('当前验证码错误或已过期!')

        return val


class CodeCheckForm(forms.Form):
    phone = forms.CharField(label='手机号', validators=[mobile_validate, ],
                            error_messages={'required': '当前字段必填!'})

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_phone(self):
        """
        手机号的钩子校验函数
        """
        clean_phone = self.cleaned_data['phone']
        # 从数据库中校验手机号
        result = RegisterUserInfo.objects.filter(phone=clean_phone).exists()

        # 短信登录验证和注册验证码公用一个校验 但校验判断条件不同
        if self.request.GET.get('type') == 'login':
            if not result:
                raise ValidationError('当前手机号未注册!')

        if result:
            raise ValidationError("当前手机号已注册!")

        random_code = random.randrange(100000, 999999)

        code = sms.return_register_code(clean_phone, random_code)

        # 验证码存入redis中
        conn = get_redis_connection('default')
        conn.set(clean_phone, code, ex=60)

        return clean_phone


class SmsLoginForm(WidgetAttrsForm, forms.Form):
    phone = forms.CharField(label='手机号', validators=[mobile_validate, ])
    code = forms.CharField(label='验证码')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        usr = RegisterUserInfo.objects.filter(phone=phone).exists()
        if not usr:
            raise ValidationError('当前手机号未注册, 请注册后登录!')

        return phone

    def clean_code(self):
        code = self.cleaned_data.get('code')
        phone = self.cleaned_data.get('phone')

        # 到redis缓存中校验验证码
        conn = get_redis_connection()
        redis_code = conn.get(phone).decode('utf-8')

        if redis_code != code:
            raise ValidationError('验证码错误或者过期, 请重新获取验证码')

        return code


class NormalLoginForm(WidgetAttrsForm, forms.Form):
    email_or_phone = forms.CharField(label='邮箱或手机号')
    pwd = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True), )
    code = forms.CharField(label='验证码')

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_email_or_phone(self):
        usr = self.cleaned_data.get('email_or_phone')
        # 密码查询 输入的必须是密文的密码
        pwd = hashlib.md5(self.cleaned_data.get('pwd').encode('utf-8')).hexdigest()
        # 组合搜索条件 输入手机或者邮箱来查询用户对象
        usr_obj = RegisterUserInfo.objects.filter(Q(email=usr)|Q(phone=usr)).filter(pwd=pwd).first()
        if not usr_obj:
            return ValidationError('当前用户名不存在或密码错误!')

        return usr_obj

    def clean_code(self):
        # 将输入的验证码和session中存储的验证码进行比较
        code = self.cleaned_data.get('code')
        session_code = self.request.session.get('code')

        if not session_code:
            raise ValidationError('当前图片验证码已经过期!')

        if code.lower() != session_code.lower():
            raise ValidationError('验证码输入错误!请重新输入!')

        return code
