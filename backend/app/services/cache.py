import hashlib
import json
from typing import Any
from app.core.config import settings

try:
    import redis.asyncio as redis
except Exception:
    redis = None

_memory_cache: dict[str, str] = {}
_client = redis.from_url(settings.redis_url, decode_responses=True) if redis else None

def make_cache_key(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return "analysis:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

async def get_cache(key: str) -> dict | None:
    if _client:
        try:
            value = await _client.get(key)
            return json.loads(value) if value else None
        except Exception:
            pass
    value = _memory_cache.get(key)
    return json.loads(value) if value else None

async def set_cache(key: str, value: dict) -> None:
    raw = json.dumps(value, ensure_ascii=False, default=str)
    if _client:
        try:
            await _client.set(key, raw, ex=settings.cache_ttl_seconds)
            return
        except Exception:
            pass
    _memory_cache[key] = raw
