"""Speech-to-text using faster-whisper."""

from __future__ import annotations

import threading
from typing import Callable, Optional

import numpy as np

from ..utils.logger import get_logger

log = get_logger("audio.transcriber")


class Transcriber:
    """Wraps faster-whisper for low-latency transcription."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        language: Optional[str] = None,
        on_transcript: Optional[Callable[[str], None]] = None,
    ):
        self._model_size = model_size
        self._device = device
        self._language = language
        self._on_transcript = on_transcript
        self._model = None
        self._lock = threading.Lock()
        self._load_thread = threading.Thread(target=self._load_model, daemon=True)
        self._load_thread.start()

    def _load_model(self) -> None:
        try:
            from faster_whisper import WhisperModel
            log.info("Loading Whisper model '%s' on %s…", self._model_size, self._device)
            with self._lock:
                self._model = WhisperModel(
                    self._model_size,
                    device=self._device,
                    compute_type="int8" if self._device == "cpu" else "float16",
                )
            log.info("Whisper model loaded.")
        except ImportError:
            log.error("faster-whisper not installed. Run: pip install faster-whisper")
        except Exception as e:
            log.error("Model load failed: %s", e)

    @property
    def ready(self) -> bool:
        return self._model is not None

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> Optional[str]:
        """Synchronously transcribe a numpy audio array."""
        with self._lock:
            if not self._model:
                log.warning("Whisper model not yet loaded")
                return None
            try:
                segments, _ = self._model.transcribe(
                    audio,
                    language=self._language,
                    beam_size=5,
                    vad_filter=True,
                    vad_parameters={"min_silence_duration_ms": 500},
                )
                text = " ".join(seg.text.strip() for seg in segments).strip()
                return text if text else None
            except Exception as e:
                log.error("Transcription error: %s", e)
                return None

    def transcribe_async(self, audio: np.ndarray, sample_rate: int = 16000) -> None:
        """Transcribe in a background thread and call on_transcript when done."""
        def _run():
            text = self.transcribe(audio, sample_rate)
            if text and self._on_transcript:
                self._on_transcript(text)

        threading.Thread(target=_run, daemon=True).start()
