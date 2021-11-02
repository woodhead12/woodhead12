# ============ 缓存数据库redis配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
        }
    }
}

COS_SECRET_ID = 'AKIDpUt2uVprd7KGwLTKu41PXP0KNGsDH4cs'
COS_SECRET_KEY = '0jCOL1ScV7SXLs76oFPIvHNCl34oHTO1'
COS_REGION = 'ap-nanjing'