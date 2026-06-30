"""Audio recording — captures microphone input into chunks for transcription."""

from __future__ import annotations

import queue
import threading
import time
from typing import Callable, Optional

import numpy as np

from ..utils.logger import get_logger
from ..config.settings import get_settings

log = get_logger("audio.recorder")


class AudioRecorder:
    """Continuously records audio and emits chunks for transcription.

    The recorder splits audio into segments whenever it detects a pause
    (silence longer than `pause_duration` seconds), which typically
    corresponds to the end of a sentence or question.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_seconds: float = 3.0,
        silence_threshold: float = 0.01,
        pause_duration: float = 1.5,
        on_chunk: Optional[Callable[[np.ndarray], None]] = None,
    ):
        self._sample_rate = sample_rate
        self._chunk_size = int(sample_rate * 0.1)  # 100ms frames
        self._silence_threshold = silence_threshold
        self._pause_duration = pause_duration
        self._on_chunk = on_chunk

        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._buffer: list[np.ndarray] = []
        self._last_sound_time: float = 0.0

    def start(self, on_chunk: Optional[Callable[[np.ndarray], None]] = None) -> None:
        if on_chunk:
            self._on_chunk = on_chunk
        if self._running:
            return
        self._running = True
        self._paused = False
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        log.info("AudioRecorder started (sr=%d, pause=%.1fs)", self._sample_rate, self._pause_duration)

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        log.info("AudioRecorder stopped")

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False
        self._last_sound_time = time.time()

    def _is_silent(self, data: np.ndarray) -> bool:
        return float(np.abs(data).mean()) < self._silence_threshold

    def _flush(self) -> None:
        if self._buffer and self._on_chunk:
            audio = np.concatenate(self._buffer)
            self._buffer = []
            try:
                self._on_chunk(audio)
            except Exception as e:
                log.error("on_chunk callback error: %s", e)

    def _record_loop(self) -> None:
        try:
            import sounddevice as sd
        except ImportError:
            log.error("sounddevice not installed. Run: pip install sounddevice")
            return

        self._last_sound_time = time.time()

        def _callback(indata, frames, t, status):
            if status:
                log.debug("sounddevice status: %s", status)
            if self._paused or not self._running:
                return
            mono = indata[:, 0].copy()
            if not self._is_silent(mono):
                self._buffer.append(mono)
                self._last_sound_time = time.time()
            else:
                # Track silence — flush if pause threshold exceeded
                silence_secs = time.time() - self._last_sound_time
                if self._buffer and silence_secs >= self._pause_duration:
                    self._flush()

        try:
            with sd.InputStream(
                samplerate=self._sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self._chunk_size,
                callback=_callback,
            ):
                while self._running:
                    time.sleep(0.05)
        except Exception as e:
            log.error("Recording error: %s", e)
        finally:
            self._flush()
