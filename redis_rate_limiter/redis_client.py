from redis import Redis

from .config import settings

wrapper = dict(client=None)


def get_redis_client():  # pragma: no cover
    if wrapper["client"]:
        return wrapper["client"]
    client = Redis.from_url(settings.redis_url)
    return client
