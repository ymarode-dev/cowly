from __future__ import annotations


import redis

from app.config import settings

_client: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    global _client
    if not settings.redis_enabled:
        return None
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def is_token_blacklisted(jti: str) -> bool:
    client = get_redis()
    if not client:
        return False
    return bool(client.exists(f"access:blacklist:{jti}"))
