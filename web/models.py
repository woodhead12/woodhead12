from django.db import models


# Create your models here.

class RegisterUserInfo(models.Model):
    usr = models.CharField(verbose_name='用户名', max_length=16, db_index=True)
    email = models.EmailField(verbose_name='邮箱', max_length=16)
    pwd = models.CharField(verbose_name='密码', max_length=64)
    phone = models.CharField(verbose_name='手机号', max_length=16)

    def __str__(self):
        return self.usr


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

    bucket = models.CharField(verbose_name='cos桶', max_length=128)
    region = models.CharField(verbose_name='cos区域', max_length=16)


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


class WikiArticle(models.Model):
    title = models.CharField(verbose_name='标题', max_length=64)
    content = models.TextField(verbose_name='内容', max_length=128)

    depth = models.SmallIntegerField(verbose_name='文章深度', default=1)

    project = models.ForeignKey(to="ProjectDetail", on_delete=models.DO_NOTHING, null=True, blank=True)
    parent_wiki = models.ForeignKey(to='self', on_delete=models.DO_NOTHING, null=True, blank=True)


class FileUpdate(models.Model):
    file_type_choices = (
        (1, '文件'),
        (2, '文件夹')
    )

    file_type = models.SmallIntegerField(verbose_name='文件类型', choices=file_type_choices)
    name = models.CharField(verbose_name='文件夹名称', max_length=32)
    key = models.CharField(verbose_name='存储在cos桶中的key', max_length=128, null=True, blank=True)
    file_size = models.IntegerField(verbose_name='文件大小', null=True, blank=True)

    # 即存储在腾讯桶中的 访问文件的路径
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True, blank=True)

    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True, related_name='child')
    update_user = models.ForeignKey(to='RegisterUserInfo', on_delete=models.DO_NOTHING, verbose_name='最近更新者')
    update_datetime = models.DateTimeField(verbose_name='最近更新时间', auto_now=True)
    project = models.ForeignKey(to='ProjectDetail', verbose_name='项目', on_delete=models.DO_NOTHING)


class Issues(models.Model):
    """ 问题 """
    project = models.ForeignKey(verbose_name='项目', to='ProjectDetail', on_delete=models.DO_NOTHING)
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType', on_delete=models.DO_NOTHING)
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True, on_delete=models.DO_NOTHING)

    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    )
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    # 新建、处理中、已解决、已忽略、待反馈、已关闭、重新打开
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)

    assign = models.ForeignKey(verbose_name='指派', to='RegisterUserInfo', related_name='task', null=True, blank=True, on_delete=models.DO_NOTHING)
    attention = models.ManyToManyField(verbose_name='关注者', to='RegisterUserInfo', related_name='observe', blank=True)

    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.DO_NOTHING)

    creator = models.ForeignKey(verbose_name='创建者', to='RegisterUserInfo', related_name='create_problems', on_delete=models.DO_NOTHING)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


class Module(models.Model):
    """ 模块（里程碑）"""
    project = models.ForeignKey(verbose_name='项目', to='ProjectDetail', on_delete=models.DO_NOTHING)
    title = models.CharField(verbose_name='模块名称', max_length=32)

    def __str__(self):
        return self.title


class IssuesType(models.Model):
    """ 问题类型 例如：任务、功能、Bug """

    PROJECT_INIT_LIST = ["任务", '功能', 'Bug']

    title = models.CharField(verbose_name='类型名称', max_length=32)
    project = models.ForeignKey(verbose_name='项目', to='ProjectDetail', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title


