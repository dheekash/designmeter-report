"""OpenAI provider."""

from __future__ import annotations

from typing import Generator

from ..base import AIProvider
from ...utils.logger import get_logger

log = get_logger("ai.openai")


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self._api_key = api_key
        self._model = model
        self._client = None

    def _get_client(self):
        if not self._client:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self._api_key)
            except ImportError:
                raise RuntimeError("openai package not installed. Run: pip install openai")
        return self._client

    @property
    def name(self) -> str:
        return f"openai/{self._model}"

    def is_available(self) -> bool:
        return bool(self._api_key)

    def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        try:
            client = self._get_client()
            resp = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            log.error("OpenAI error: %s", e)
            raise

    def stream(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> Generator[str, None, None]:
        try:
            client = self._get_client()
            stream = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            log.error("OpenAI stream error: %s", e)
            raise
