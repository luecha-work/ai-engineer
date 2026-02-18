import json
import redis

from app.config.settings import settings


redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def cache_get(key: str):
    value = redis_client.get(key)
    if value is None:
        return None
    return json.loads(value)


def cache_set(key: str, value: dict, ttl: int):
    redis_client.setex(key, ttl, json.dumps(value))
