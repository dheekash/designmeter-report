"""Application core — wires audio, AI, database, OCR, and hotkeys together."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, Optional

from .config.settings import Settings, get_settings
from .ai import build_provider, AnswerGenerator
from .audio.recorder import AudioRecorder
from .audio.transcriber import Transcriber
from .database.repository import Repository
from .ocr.engine import OCREngine
from .hotkeys.manager import HotkeyManager
from .utils.cache import ResponseCache
from .utils.logger import get_logger, setup_logger

log = get_logger("app")


class AppCore:
    """Central application object — owns all services."""

    def __init__(self):
        self.settings: Settings = get_settings()

        # Logging
        setup_logger(level=self.settings.log_level, log_file=self.settings.log_file)

        # Database
        self.repository = Repository(self.settings.db_path)

        # Cache
        self._cache = ResponseCache(max_size=self.settings.cache_max_size)

        # AI
        self._provider = build_provider(self.settings)
        self.generator = AnswerGenerator(
            self._provider,
            resume_text=self._load_resume(),
        )

        # Audio
        self._transcriber = Transcriber(
            model_size=self.settings.whisper_model,
            device=self.settings.whisper_device,
            language=self.settings.whisper_language,
            on_transcript=self._handle_transcript,
        )
        self._recorder = AudioRecorder(
            sample_rate=self.settings.audio_sample_rate,
            chunk_seconds=self.settings.audio_chunk_seconds,
            silence_threshold=self.settings.audio_silence_threshold,
            pause_duration=self.settings.audio_pause_duration,
            on_chunk=self._transcriber.transcribe_async,
        )

        # OCR
        self.ocr_engine = OCREngine(
            engine=self.settings.ocr_engine,
            tesseract_path=self.settings.tesseract_path,
        )

        # Hotkeys
        self._hotkeys = HotkeyManager()

        # UI callbacks (set by MainWindow)
        self._on_transcript: Optional[Callable[[str], None]] = None
        self._on_status: Optional[Callable[[str], None]] = None

        self.is_listening = False
        log.info("AppCore initialised — provider=%s", self._provider.name)

    # ------------------------------------------------------------------ #

    def set_ui_callbacks(
        self,
        on_transcript: Callable[[str], None],
        on_status: Callable[[str], None],
    ):
        self._on_transcript = on_transcript
        self._on_status = on_status

        # Wire hotkeys now that we have UI callbacks
        self._hotkeys.register("start_listening", self.start_listening)
        self._hotkeys.register("stop_listening", self.stop_listening)
        self._hotkeys.start()

    # ------------------------------------------------------------------ #
    #  Audio / Speech                                                      #
    # ------------------------------------------------------------------ #

    def start_listening(self):
        if self.is_listening:
            return
        self.is_listening = True
        if self._on_status:
            self._on_status("listening")
        log.info("Started listening")
        self._recorder.start()

    def stop_listening(self):
        if not self.is_listening:
            return
        self.is_listening = False
        self._recorder.stop()
        if self._on_status:
            self._on_status("ready")
        log.info("Stopped listening")

    def _handle_transcript(self, text: str):
        log.info("Transcript: %s", text[:80])
        if self._on_transcript:
            self._on_transcript(text)

    # ------------------------------------------------------------------ #
    #  Provider management                                                 #
    # ------------------------------------------------------------------ #

    def rebuild_provider(self):
        self._provider = build_provider(self.settings)
        self.generator = AnswerGenerator(
            self._provider,
            resume_text=self._load_resume(),
        )
        log.info("Provider rebuilt → %s", self._provider.name)

    # ------------------------------------------------------------------ #
    #  Resume                                                              #
    # ------------------------------------------------------------------ #

    def _load_resume(self) -> Optional[str]:
        path = self.settings.resume_path
        if not path:
            return None
        p = Path(path)
        if not p.exists():
            return None
        try:
            if p.suffix.lower() == ".pdf":
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(str(p))
                    return "\n".join(page.get_text() for page in doc)
                except ImportError:
                    pass
            return p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            log.warning("Could not load resume: %s", e)
            return None

    # ------------------------------------------------------------------ #
    #  Shutdown                                                            #
    # ------------------------------------------------------------------ #

    def shutdown(self):
        log.info("Shutting down…")
        self.stop_listening()
        self._hotkeys.stop()
