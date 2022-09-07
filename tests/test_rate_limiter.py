import datetime
from unittest import mock

import freezegun
import pytest
from fakeredis import FakeStrictRedis
from hypothesis import given
from hypothesis import strategies as st

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


@pytest.mark.noredismock
@given(st.text().filter(lambda x: x != '' and x != 0))
def test_check_str(value):
    client = FakeStrictRedis()  # Explicitly overwrite the client as hypothesis doesn't work with fixtures
    with mock.patch(
        "redis_rate_limiter.redis_client.get_redis_client", autospec=True
    ) as mocked_get_redis_client:
        mocked_get_redis_client.return_value = client

        print(value)
        limit = 10
        rate_limiter = RateLimiter(limit, period=10)
        for i in range(limit):
            rate_limiter.check_str(value)
        with pytest.raises(RateLimitExceeded):
            rate_limiter.check_str(value)  # The call above the rate limit
