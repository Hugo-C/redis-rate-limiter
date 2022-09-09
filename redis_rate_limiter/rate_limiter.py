import functools
import sys
import time
from datetime import timedelta
from typing import Callable, Union

from redis_rate_limiter import redis_client

from .config import settings
from .exceptions import RateLimitExceeded


class RateLimiter:
    def __init__(
        self,
        limit: int = sys.maxsize,
        period: Union[int, timedelta] = timedelta(minutes=1),
    ):
        """RateLimiter

        :param limit: Rate limit for each period, defaults to sys.maxsize
        :type limit: int, optional
        :param period: Size of the period, accept int(seconds) and timedelta, defaults to timedelta(minutes=1)
        :type period: Union[int, timedelta], optional
        """
        self.redis_client = redis_client.get_redis_client()
        self.limit = limit
        self.period = period.seconds if isinstance(period, timedelta) else period

    def check(self, func: Callable):
        """Check if func could be called.

        :param func: the func to be limited
        :type func: Callable
        :raises RateLimitExceeded: Raised when the func has been called `self.limit` times during last `self.period`
        """
        self.check_str(func.__name__)

    def check_str(self, value: str):
        """Check if a given value has been check less than the rate limit

        :param value: the value to check
        :type value: str
        :raises RateLimitExceeded: Raised when the value has been checked `self.limit` times during last `self.period`
        """
        key = f"{settings.key_prefix}:{value}:{int(time.time())//self.period}"
        if int(self.redis_client.incr(key)) > self.limit:
            raise RateLimitExceeded()
        if self.redis_client.ttl(key) == -1:
            self.redis_client.expire(key, self.period)

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.check(func)
            return func(*args, **kwargs)

        return wrapper
