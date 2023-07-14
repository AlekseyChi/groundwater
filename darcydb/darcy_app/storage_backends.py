from storages.backends.s3boto3 import S3Boto3Storage


class YandexObjectStorage(S3Boto3Storage):
    endpoint_url = "https://storage.yandexcloud.net"
    default_acl = "public-read"  # or set as per your requirements
