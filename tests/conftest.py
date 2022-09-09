from unittest import mock

import pytest
from fakeredis import FakeStrictRedis

from redis_rate_limiter import redis_client  # noqa required by fixture


@pytest.fixture(autouse=True)
def mock_redis_client(request):
    if "noredismock" in request.keywords:
        # If @pytest.mark.noredismock is set, skip the mock and return
        yield None
        return
    client = FakeStrictRedis()
    with mock.patch(
        "redis_rate_limiter.redis_client.get_redis_client", autospec=True
    ) as mocked_get_redis_client:
        mocked_get_redis_client.return_value = client
        yield client
