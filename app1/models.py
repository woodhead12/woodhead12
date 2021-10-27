from django.db import models


# Create your models here.

class RegisterUserInfo(models.Model):
    usr = models.CharField(verbose_name='用户名', max_length=16)
    email = models.EmailField(verbose_name='邮箱', max_length=16)
    pwd = models.CharField(verbose_name='密码', max_length=16)
    phone = models.CharField(verbose_name='手机号', max_length=16)


class ProjectManageService(models.Model):
    type = models.CharField(verbose_name='分类', max_length=16)
    desc = models.CharField(verbose_name='描述', max_length=64)
    price = models.IntegerField(verbose_name='价格')
    count = models.IntegerField(verbose_name='项目上限')
    member = models.IntegerField(verbose_name='邀请成员上限')
    space = models.IntegerField(verbose_name='项目空间(M)')
    file_limit = models.IntegerField(verbose_name='单文件上传上限')
    create_time = models.DateTimeField(verbose_name='创建时间')

    def __str__(self):
        return self.type


class PayingRecord(models.Model):
    type = models.CharField(verbose_name='分类', max_length=16)
    real_pay = models.IntegerField(verbose_name='实际支付')
    begin = models.DateTimeField(verbose_name='服务开始时间')
    end = models.DateTimeField(verbose_name='服务结束时间', blank=True, null=True)

    usr = models.ForeignKey(to='RegisterUserInfo', on_delete=models.DO_NOTHING)
    service = models.ForeignKey(to='ProjectManageService', on_delete=models.DO_NOTHING)


class ProjectDetail(models.Model):
    name = models.CharField(verbose_name='项目名称', max_length=16)
    desc = models.CharField(verbose_name='项目描述', max_length=64)
    color = models.CharField(verbose_name='颜色', max_length=16)
    star = models.BooleanField(verbose_name='星标')
    member = models.IntegerField(verbose_name='项目参与人数')
    used_space = models.IntegerField(verbose_name='已使用空间')

    creator = models.ForeignKey(to='RegisterUserInfo', on_delete=models.DO_NOTHING)


class InProjectDetail(models.Model):
    usr = models.ForeignKey(to='RegisterUserInfo', on_delete=models.DO_NOTHING)
    project = models.ForeignKey(to='ProjectDetail', on_delete=models.DO_NOTHING)

