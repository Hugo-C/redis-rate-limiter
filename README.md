# redis-rate-limiter

## Install

```bash
pip install -U redis-rate-limiter
```

## Use

```python
from redis_rate_limiter.rate_limiter import RateLimiter

@RateLimiter(10, period=1)
def greet():
    print('Hello')

for _ in range(100):
    greet()

# Raise RateLimitExceeded after print('Hello') 10 times
```
