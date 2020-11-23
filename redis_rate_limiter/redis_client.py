from redis import Redis
from .config import settings


def get_redis_client():
    client = Redis.from_url(settings.redis_url)
    assert client.ping()
    return client


redis_client = get_redis_client()
