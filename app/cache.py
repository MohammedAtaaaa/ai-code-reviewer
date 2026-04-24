"""Redis caching layer for code review results."""

import hashlib
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    """Lazily connect to Redis. Returns None if unavailable."""
    global _redis_client
    if not settings.redis_enabled:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import redis

        _redis_client = redis.Redis.from_url(
            settings.redis_url, decode_responses=True, socket_timeout=2
        )
        _redis_client.ping()
        logger.info("Redis connected at %s", settings.redis_url)
        return _redis_client
    except Exception:
        logger.warning("Redis unavailable — caching disabled")
        _redis_client = None
        return None


def code_hash(code: str, language: str) -> str:
    """Produce a deterministic hash for a code + language pair."""
    content = f"{language}:{code}"
    return hashlib.sha256(content.encode()).hexdigest()


def get_cached_review(cache_key: str) -> dict | None:
    """Retrieve a cached review result by key."""
    client = _get_redis()
    if client is None:
        return None
    try:
        data = client.get(f"review:{cache_key}")
        if data:
            logger.debug("Cache hit for %s", cache_key[:12])
            return json.loads(data)
    except Exception:
        logger.warning("Redis read error for key %s", cache_key[:12])
    return None


def set_cached_review(cache_key: str, result: dict) -> None:
    """Store a review result in cache."""
    client = _get_redis()
    if client is None:
        return
    try:
        client.setex(
            f"review:{cache_key}",
            settings.redis_ttl_seconds,
            json.dumps(result, default=str),
        )
        logger.debug("Cached result for %s", cache_key[:12])
    except Exception:
        logger.warning("Redis write error for key %s", cache_key[:12])
