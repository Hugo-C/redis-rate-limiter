# redis-rate-limiter

[![CI](https://github.com/duyixian1234/redis-rate-limiter/actions/workflows/CI.yml/badge.svg?branch=master)](https://github.com/duyixian1234/redis-rate-limiter/actions/workflows/CI.yml)

## Install

```bash
pip install -U redis-rate-limiter
```

## Use

```python
from redis_rate_limiter.config import basic_config
from redis_rate_limiter.rate_limiter import RateLimiter

basic_config(redis_url='redis://localhost:6379/0')

@RateLimiter(10, period=1)
def greet():
    print('Hello')

for _ in range(100):
    greet()

# Raise RateLimitExceeded after print('Hello') 10 times
```
