from django.db import models


# Create your models here.

class RegisterUserInfo(models.Model):
    usr = models.CharField(verbose_name='用户名', max_length=16, db_index=True)
    email = models.EmailField(verbose_name='邮箱', max_length=16)
    pwd = models.CharField(verbose_name='密码', max_length=64)
    phone = models.CharField(verbose_name='手机号', max_length=16)


class ProjectManageService(models.Model):
    """
    价格策略
    """
    category_choices = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    )

    # smallInteger 小范围整型
    type = models.SmallIntegerField(verbose_name='收费类型', choices=category_choices)
    desc = models.CharField(verbose_name='描述', max_length=64)

    # positiveInteger 正整数类型
    price = models.PositiveIntegerField(verbose_name='价格')
    count = models.PositiveIntegerField(verbose_name='项目上限')
    member = models.PositiveIntegerField(verbose_name='邀请成员上限')
    space = models.PositiveIntegerField(verbose_name='项目空间(M)')
    file_limit = models.PositiveIntegerField(verbose_name='单文件上传上限')

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class PayingRecord(models.Model):
    """
    交易记录相关
    """
    status_choice = (
        (1, '未支付'),
        (2, '已支付')
    )

    type = models.SmallIntegerField(verbose_name='支付状态', choices=status_choice)
    # 设置了唯一索引
    order = models.CharField(verbose_name='订单号', max_length=64, unique=True)

    real_pay = models.IntegerField(verbose_name='实际支付')
    count = models.IntegerField(verbose_name='数量(年)', help_text='为0表示无限期')

    begin = models.DateTimeField(verbose_name='服务开始时间', blank=True, null=True)
    end = models.DateTimeField(verbose_name='服务结束时间', blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    usr = models.ForeignKey(verbose_name='用户', to='RegisterUserInfo', on_delete=models.DO_NOTHING)
    service = models.ForeignKey(verbose_name='价格策略', to='ProjectManageService', on_delete=models.DO_NOTHING)


class ProjectDetail(models.Model):
    """
    项目详情
    """
    COLOR_CHOICES = (
        (1, "#56b8eb"),
        (2, "#f28033"),
        (3, "#ebc656"),
        (4, "#a2dl48"),
        (5, "#20BFA4"),
        (6, "#7461c2"),
        (7, "#20bfa3"),
    )

    name = models.CharField(verbose_name='项目名称', max_length=64)
    desc = models.CharField(verbose_name='项目描述', max_length=128)

    color = models.SmallIntegerField(verbose_name='颜色', choices=COLOR_CHOICES, default=1)
    star = models.BooleanField(verbose_name='星标', default=False)

    member = models.SmallIntegerField(verbose_name='项目参与人数', default=1)
    used_space = models.IntegerField(verbose_name='已使用空间', default=0)

    creator = models.ForeignKey(verbose_name='创建者', to='RegisterUserInfo', on_delete=models.DO_NOTHING)


class InProjectDetail(models.Model):
    """
    项目参与者
    """

    usr = models.ForeignKey(verbose_name='用户', to='RegisterUserInfo', on_delete=models.DO_NOTHING)
    project = models.ForeignKey(verbose_name='项目', to='ProjectDetail', on_delete=models.DO_NOTHING)

    # invitee = models.ForeignKey(verbose_name='邀请者', to='RegisterUserInfo', related_name='invites',
    #                             blank=True, null=True, on_delete=models.DO_NOTHING)

    star = models.BooleanField(verbose_name='星标', default=False)
    create_time = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)
