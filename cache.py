import json
import os
import threading
from typing import Any, Optional

_UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
_UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
_KEY_PREFIX = "eurlex:"


class _RedisCache:
    def __init__(self, url: str, token: str):
        from upstash_redis import Redis
        self._r = Redis(url=url, token=token)

    def get(self, celex_id: str) -> Optional[Any]:
        val = self._r.get(f"{_KEY_PREFIX}{celex_id.lower()}")
        return json.loads(val) if val else None

    def set(self, celex_id: str, value: Any) -> None:
        self._r.set(f"{_KEY_PREFIX}{celex_id.lower()}", json.dumps(value))

    def size(self) -> int:
        return -1  # distributed cache; size not tracked locally


class _MemoryCache:
    def __init__(self):
        self._store: dict[str, Any] = {}
        self._lock = threading.Lock()

    def get(self, celex_id: str) -> Optional[Any]:
        with self._lock:
            return self._store.get(celex_id.lower())

    def set(self, celex_id: str, value: Any) -> None:
        with self._lock:
            self._store[celex_id.lower()] = value

    def size(self) -> int:
        with self._lock:
            return len(self._store)


if _UPSTASH_URL and _UPSTASH_TOKEN:
    cache = _RedisCache(_UPSTASH_URL, _UPSTASH_TOKEN)
else:
    cache = _MemoryCache()
