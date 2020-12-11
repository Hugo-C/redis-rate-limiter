from redis import Redis

from redis_rate_limiter.exceptions import ConfigError

from .config import settings

wrapper = dict(client=None)


def get_redis_client():
    if wrapper["client"]:
        return wrapper["client"]
    client = Redis.from_url(settings.redis_url)
    return client
