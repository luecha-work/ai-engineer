from typing import Optional, Any
import json
import redis
from langchain_redis import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from app.config.settings import settings


def get_redis_memory(
    session_id: str,
    k: int = 5,
    key_prefix: str = "chat_history",
    ttl: int = 3600,
) -> ConversationBufferWindowMemory:
    if not session_id:
        raise ValueError("session_id is required for memory persistence")

    redis_client = redis.from_url(settings.redis_url, decode_responses=True)

    chat_history = RedisChatMessageHistory(
        session_id=session_id,
        redis_client=redis_client,
        key_prefix=key_prefix,
        ttl=ttl,
    )

    return ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=k,
        chat_memory=chat_history,
    )


def clear_redis_memory(
    session_id: str,
    key_prefix: str = "chat_history",
):
    if not session_id:
        raise ValueError("session_id is required for memory persistence")

    key = f"{key_prefix}{session_id}"
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    redis_client.delete(key)


def create_redis_memory(
    session_id: str,
    k: int = 5,
    limit: Optional[int] = None,
    key_prefix: str = "chat_history:",
    memory_key: str = "history_store",
    ttl: Optional[int] = None,
) -> ConversationBufferWindowMemory:
    """
    Create a ConversationBufferWindowMemory backed by Redis.
    Optionally trim Redis if `limit` is set.
    """
    if not session_id:
        raise ValueError("session_id is required for memory persistence")

    redis_client = redis.from_url(settings.redis_url, decode_responses=True)

    """key_prefix must begin with chat_history"""
    chat_history = RedisChatMessageHistory(
        session_id=session_id,
        redis_client=redis_client,
        key_prefix=key_prefix,
        ttl=ttl,
    )

    # if limit is not None:
    #     key = f"{key_prefix}{session_id}"
    #     redis_client.ltrim(key, -limit * 2, -1)

    return ConversationBufferWindowMemory(
        memory_key=memory_key,
        return_messages=True,
        k=k,
        chat_memory=chat_history,
    )


def cache_get(key: str) -> Optional[Any]:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    value = redis_client.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def cache_set(key: str, value: Any, ttl_seconds: int | None = None) -> None:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    payload = value
    if not isinstance(value, str):
        payload = json.dumps(value)
    if ttl_seconds:
        redis_client.setex(key, ttl_seconds, payload)
    else:
        redis_client.set(key, payload)
