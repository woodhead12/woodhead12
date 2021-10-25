from django.db import models


# Create your models here.

class RegisterUserInfo(models.Model):
    usr = models.CharField(verbose_name='用户名', max_length=16, db_index=True)
    email = models.EmailField(verbose_name='邮箱', max_length=16)
    pwd = models.CharField(verbose_name='密码', max_length=16)
    phone = models.CharField(verbose_name='手机号', max_length=16)
