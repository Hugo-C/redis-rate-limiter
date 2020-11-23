from dataclasses import dataclass, field
import socket
import os


@dataclass
class Settings:
    redis_url: str = os.getenv("REDIS_RATE_LIMITER_DSN", "redis://localhost:6379/0")
    key_prefix: str = field(default_factory=socket.gethostname)


settings = Settings()
