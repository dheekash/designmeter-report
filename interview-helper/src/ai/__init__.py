from .base import AIProvider
from .detector import detect_category
from .generator import AnswerGenerator
from .providers import OpenAIProvider, ClaudeProvider, GeminiProvider, OllamaProvider

__all__ = [
    "AIProvider", "detect_category", "AnswerGenerator",
    "OpenAIProvider", "ClaudeProvider", "GeminiProvider", "OllamaProvider",
]


def build_provider(settings) -> AIProvider:
    """Factory: pick provider from settings."""
    p = settings.active_provider()
    if p == "openai":
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    if p == "claude":
        return ClaudeProvider(settings.anthropic_api_key, settings.claude_model)
    if p == "gemini":
        return GeminiProvider(settings.gemini_api_key, settings.gemini_model)
    return OllamaProvider(settings.ollama_base_url, settings.ollama_model)
