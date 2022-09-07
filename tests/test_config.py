from redis_rate_limiter.config import basic_config, settings

def test_basic_config():
    basic_config("redis://remote-addr:6379/0", key_prefix="PREFIX:")
    assert settings.redis_url == "redis://remote-addr:6379/0"
    assert settings.key_prefix == "PREFIX:"
