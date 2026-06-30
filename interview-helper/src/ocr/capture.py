"""Screen capture with region selection overlay."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from PIL import Image

from ..utils.logger import get_logger

log = get_logger("ocr.capture")


def capture_region(region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Image.Image]:
    """Capture a region of the screen.

    Args:
        region: (left, top, width, height) or None for full screen.

    Returns:
        PIL Image or None on failure.
    """
    try:
        import mss
        import mss.tools

        with mss.mss() as sct:
            if region:
                left, top, width, height = region
                monitor = {"left": left, "top": top, "width": width, "height": height}
            else:
                monitor = sct.monitors[1]  # primary monitor

            shot = sct.grab(monitor)
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            return img
    except Exception as e:
        log.error("Screen capture failed: %s", e)
        return None


def capture_fullscreen() -> Optional[Image.Image]:
    return capture_region(None)


def save_capture(image: Image.Image, path: Path) -> Path:
    image.save(str(path))
    return path
