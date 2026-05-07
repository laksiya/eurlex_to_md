import threading
from typing import Any


class DocumentCache:
    def __init__(self):
        self._store: dict[str, Any] = {}
        self._lock = threading.Lock()

    def get(self, celex_id: str) -> Any:
        with self._lock:
            return self._store.get(celex_id.lower())

    def set(self, celex_id: str, value: Any) -> None:
        with self._lock:
            self._store[celex_id.lower()] = value

    def size(self) -> int:
        with self._lock:
            return len(self._store)


cache = DocumentCache()
