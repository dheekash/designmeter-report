"""Anthropic Claude provider."""

from __future__ import annotations

from typing import Generator

from ..base import AIProvider
from ...utils.logger import get_logger

log = get_logger("ai.claude")


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._api_key = api_key
        self._model = model
        self._client = None

    def _get_client(self):
        if not self._client:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                raise RuntimeError("anthropic package not installed. Run: pip install anthropic")
        return self._client

    @property
    def name(self) -> str:
        return f"claude/{self._model}"

    def is_available(self) -> bool:
        return bool(self._api_key)

    def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        try:
            client = self._get_client()
            msg = client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            log.error("Claude error: %s", e)
            raise

    def stream(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> Generator[str, None, None]:
        try:
            client = self._get_client()
            with client.messages.stream(
                model=self._model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as s:
                for text in s.text_stream:
                    yield text
        except Exception as e:
            log.error("Claude stream error: %s", e)
            raise
