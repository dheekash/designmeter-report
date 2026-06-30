"""Ollama local model provider (offline support)."""

from __future__ import annotations

from typing import Generator

import requests

from ..base import AIProvider
from ...utils.logger import get_logger

log = get_logger("ai.ollama")


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self._base_url = base_url.rstrip("/")
        self._model = model

    @property
    def name(self) -> str:
        return f"ollama/{self._model}"

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self._base_url}/api/tags", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        try:
            r = requests.post(f"{self._base_url}/api/chat", json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["message"]["content"]
        except Exception as e:
            log.error("Ollama error: %s", e)
            raise

    def stream(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> Generator[str, None, None]:
        import json as _json

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
        }
        try:
            with requests.post(f"{self._base_url}/api/chat", json=payload, stream=True, timeout=120) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        data = _json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if data.get("done"):
                            break
        except Exception as e:
            log.error("Ollama stream error: %s", e)
            raise
