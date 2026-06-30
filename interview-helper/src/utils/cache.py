"""LRU cache for AI responses — avoids re-querying identical questions."""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from typing import Any, Optional


class ResponseCache:
    def __init__(self, max_size: int = 500):
        self._max_size = max_size
        self._store: OrderedDict[str, dict] = OrderedDict()

    def _key(self, question: str, category: str, provider: str) -> str:
        raw = f"{provider}::{category}::{question.strip().lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def get(self, question: str, category: str, provider: str) -> Optional[dict]:
        k = self._key(question, category, provider)
        if k in self._store:
            entry = self._store[k]
            if time.time() - entry["ts"] < 3600 * 24:  # 24-hour TTL
                self._store.move_to_end(k)
                return entry["data"]
            del self._store[k]
        return None

    def set(self, question: str, category: str, provider: str, data: dict) -> None:
        k = self._key(question, category, provider)
        self._store[k] = {"data": data, "ts": time.time()}
        self._store.move_to_end(k)
        if len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
