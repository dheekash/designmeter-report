"""Abstract base class for all AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generator, Optional


class AIProvider(ABC):
    """All AI providers implement this interface."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider can be used (API key set, service reachable)."""
        ...

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        """Blocking completion — return the full response string."""
        ...

    def stream(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 2048
    ) -> Generator[str, None, None]:
        """Streaming completion — yield text chunks. Default: delegate to complete()."""
        yield self.complete(system_prompt, user_prompt, max_tokens)
