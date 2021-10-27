import os
import sys
import django

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目添加到环境变量中
sys.path.append(base_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_for_sass.settings')
django.setup()

from web import models


def run():
    exists = models.ProjectManageService.objects.filter(type=1, desc='个人免费版').exists()
    if not exists:
        models.ProjectManageService.objects.create(type=1, desc='个人免费版', price=0, count=2,
                                                   member=5, space=10, file_limit=1)


if __name__ == '__main__':
    run()
