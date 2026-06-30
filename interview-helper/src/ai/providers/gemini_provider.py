"""Google Gemini provider."""

from __future__ import annotations

from typing import Generator

from ..base import AIProvider
from ...utils.logger import get_logger

log = get_logger("ai.gemini")


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        self._api_key = api_key
        self._model = model
        self._chat_model = None

    def _get_model(self):
        if not self._chat_model:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                self._chat_model = genai.GenerativeModel(self._model)
            except ImportError:
                raise RuntimeError("google-generativeai not installed. Run: pip install google-generativeai")
        return self._chat_model

    @property
    def name(self) -> str:
        return f"gemini/{self._model}"

    def is_available(self) -> bool:
        return bool(self._api_key)

    def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        try:
            model = self._get_model()
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            resp = model.generate_content(full_prompt)
            return resp.text
        except Exception as e:
            log.error("Gemini error: %s", e)
            raise

    def stream(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> Generator[str, None, None]:
        try:
            model = self._get_model()
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            for chunk in model.generate_content(full_prompt, stream=True):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            log.error("Gemini stream error: %s", e)
            raise
