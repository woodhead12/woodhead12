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
    cors_config = {
        'CORSRule': [{
            'AllowedOrigin': '*',
            'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
            'AllowedHeader': '*',
            'ExposeHeader': '*',
            'MaxAgeSeconds': 500
        }]
    }

    client.create_bucket(
        Bucket=bucket,
        ACL='private',
    )

    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def upload_to_bucket(bucket, filename, file):
    client.upload_file_from_buffer(
        Bucket=bucket,
        Key=filename,
        Body=file
    )


def delete_from_bucket(bucket, objects=None, file_key=None):
    if objects:
        client.delete_objects(bucket, Delete=objects)

    client.delete_object(bucket, file_key)


def credential(bucket, region):
    from sts.sts import Sts

    config = {
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': settings.COS_SECRET_ID,
        # 固定密钥
        'secret_key': settings.COS_SECRET_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [

            # 'name/cos:PutObject',
            # 'name/cos:PostObject',

            # 'name/cos:InitiateMultipartUpload',
            # 'name/cos:ListMultipartUploads',
            # 'name/cos:ListParts',
            # 'name/cos:UploadPart',
            # 'name/cos:CompleteMultipartUpload',
            "*"
        ],
    }

    sts = Sts(config)
    result_dict = sts.get_credential()

    return result_dict