"""Redis session store — short-term memory (TTL 1h).

Fallback: in-memory dict if Redis not available.
"""
import json
from typing import Optional

try:
    import redis
    _r = redis.Redis.from_url("redis://localhost:6379", decode_responses=True)
    _r.ping()
    _REDIS_OK = True
except Exception:
    _REDIS_OK = False

# In-memory fallback
_memory_store: dict = {}


def save_session(session_id: str, data: dict, ttl: int = 3600):
    """Save session data with TTL (seconds)."""
    if _REDIS_OK:
        _r.setex(f"session:{session_id}", ttl, json.dumps(data, ensure_ascii=False))
    else:
        _memory_store[session_id] = data


def get_session(session_id: str) -> Optional[dict]:
    """Retrieve session data."""
    if _REDIS_OK:
        raw = _r.get(f"session:{session_id}")
        return json.loads(raw) if raw else None
    return _memory_store.get(session_id)


def delete_session(session_id: str):
    """Remove session data."""
    if _REDIS_OK:
        _r.delete(f"session:{session_id}")
    else:
        _memory_store.pop(session_id, None)
