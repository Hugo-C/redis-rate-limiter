import datetime

import freezegun
import pytest
from fakeredis import FakeStrictRedis

from redis_rate_limiter.exceptions import RateLimitExceeded
from redis_rate_limiter.rate_limiter import RateLimiter


def test_mocked_redis_client():
    """Ensure the mock redis is used in the tests"""
    client = RateLimiter().redis_client
    assert isinstance(client, FakeStrictRedis)


def test_rate_limiter_below_limit():
    expected_call = 10
    call_count = 0

    @RateLimiter(expected_call, period=1)
    def f():
        nonlocal call_count
        call_count += 1
        return 42

    for _ in range(expected_call):
        assert f() == 42
    assert call_count == expected_call


def test_rate_limiter_above_limit():
    expected_successful_call = 10
    call_count = 0

    @RateLimiter(expected_successful_call, period=1)
    def f():
        nonlocal call_count
        call_count += 1
        return 42

    for _ in range(expected_successful_call):
        assert f() == 42
    with pytest.raises(RateLimitExceeded):
        f()  # The call above the rate limit
    assert call_count == expected_successful_call


def test_rate_limiter_below_limit_on_long_period():
    expected_call = 10
    call_count = 0

    @RateLimiter(expected_call, period=10)
    def f():
        nonlocal call_count
        call_count += 1
        return 42

    initial_datetime = datetime.datetime(2012, 1, 14)
    with freezegun.freeze_time(initial_datetime) as frozen_datetime:
        for _ in range(expected_call // 2):
            assert f() == 42
        frozen_datetime.tick(delta=datetime.timedelta(seconds=5))
        for _ in range(expected_call // 2):
            assert f() == 42
    assert call_count == expected_call


def test_rate_limiter_above_limit_on_long_period():
    expected_successful_call = 10
    call_count = 0

    @RateLimiter(expected_successful_call, period=10)
    def f():
        nonlocal call_count
        call_count += 1
        return 42

    initial_datetime = datetime.datetime(2012, 1, 14)
    with freezegun.freeze_time(initial_datetime) as frozen_datetime:
        for _ in range(expected_successful_call // 2):
            assert f() == 42
        frozen_datetime.tick(delta=datetime.timedelta(seconds=5))
        for _ in range(expected_successful_call // 2):
            assert f() == 42
        with pytest.raises(RateLimitExceeded):
            f()  # The call above the rate limit
    assert call_count == expected_successful_call


def test_rate_limiter_below_limit_on_long_period_repeated():
    expected_successful_call = 100
    call_count = 0

    @RateLimiter(10, period=10)
    def f():
        nonlocal call_count
        call_count += 1
        return 42

    initial_datetime = datetime.datetime(2012, 1, 14)
    with freezegun.freeze_time(initial_datetime) as frozen_datetime:
        for _ in range(10):
            for _ in range(5):
                assert f() == 42
            frozen_datetime.tick(delta=datetime.timedelta(seconds=5))
            for _ in range(5):
                assert f() == 42
            frozen_datetime.tick(delta=datetime.timedelta(seconds=5))
    assert call_count == expected_successful_call
