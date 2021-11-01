from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging

from django.conf import settings

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = settings.COS_SECRET_ID  # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
secret_key = settings.COS_SECRET_KEY  # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
region = settings.COS_REGION  # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

# 2. 获取客户端对象
client = CosS3Client(config)


def create_bucket(bucket):
    client.create_bucket(
        Bucket=bucket,
        ACL='private',
    )


def upload_to_bucket(bucket, filename, file):
    client.upload_file_from_buffer(
        Bucket=bucket,
        Key=filename,
        Body=file
    )
