"""Application settings loaded from environment / .env file."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


class Settings:
    """Central configuration object — reads from environment variables."""

    # ----- AI -------------------------------------------------------
    ai_provider: str = os.getenv("AI_PROVIDER", "openai")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    # ----- Speech ---------------------------------------------------
    whisper_model: str = os.getenv("WHISPER_MODEL", "base")
    whisper_device: str = os.getenv("WHISPER_DEVICE", "cpu")
    whisper_language: Optional[str] = os.getenv("WHISPER_LANGUAGE") or None

    audio_sample_rate: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    audio_chunk_seconds: float = float(os.getenv("AUDIO_CHUNK_SECONDS", "3"))
    audio_silence_threshold: float = float(os.getenv("AUDIO_SILENCE_THRESHOLD", "0.01"))
    audio_pause_duration: float = float(os.getenv("AUDIO_PAUSE_DURATION", "1.5"))

    # ----- OCR ------------------------------------------------------
    ocr_engine: str = os.getenv("OCR_ENGINE", "tesseract")
    tesseract_path: str = os.getenv(
        "TESSERACT_PATH", r"C:/Program Files/Tesseract-OCR/tesseract.exe"
    )

    # ----- Database -------------------------------------------------
    @property
    def db_path(self) -> Path:
        raw = os.getenv("DB_PATH", "~/.interview_helper/history.db")
        p = Path(raw).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    cache_max_size: int = int(os.getenv("CACHE_MAX_SIZE", "500"))

    # ----- UI -------------------------------------------------------
    default_theme: str = os.getenv("DEFAULT_THEME", "dark")
    default_opacity: float = float(os.getenv("DEFAULT_OPACITY", "0.92"))
    window_width: int = int(os.getenv("WINDOW_WIDTH", "540"))
    window_height: int = int(os.getenv("WINDOW_HEIGHT", "750"))
    font_size: int = int(os.getenv("FONT_SIZE", "13"))

    # ----- Logging --------------------------------------------------
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def log_file(self) -> Path:
        raw = os.getenv("LOG_FILE", "~/.interview_helper/app.log")
        p = Path(raw).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    # ----- Resume ---------------------------------------------------
    resume_path: Optional[str] = os.getenv("RESUME_PATH") or None

    def has_provider(self, provider: str) -> bool:
        """Check whether the given provider has a usable API key."""
        key_map = {
            "openai": self.openai_api_key,
            "claude": self.anthropic_api_key,
            "gemini": self.gemini_api_key,
            "ollama": "available",  # no key needed
        }
        return bool(key_map.get(provider))

    def active_provider(self) -> str:
        """Return the best available provider."""
        preferred = self.ai_provider
        if self.has_provider(preferred):
            return preferred
        for p in ("openai", "claude", "gemini", "ollama"):
            if self.has_provider(p):
                return p
        return "ollama"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
