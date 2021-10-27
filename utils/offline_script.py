import os
import sys
import django
from datetime import datetime

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目添加到环境变量中
sys.path.append(base_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_for_sass.settings')
django.setup()

from app1 import models

models.ProjectManageService.objects.create(type='免费服务', desc='普通用户', price=0, count=2,
                                           member=5, space=10, file_limit=1, create_time=datetime.now())
