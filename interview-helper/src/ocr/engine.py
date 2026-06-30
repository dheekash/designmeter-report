"""OCR text extraction from images."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

from ..utils.logger import get_logger

log = get_logger("ocr.engine")


class OCREngine:
    def __init__(self, engine: str = "tesseract", tesseract_path: Optional[str] = None):
        self._engine = engine
        self._tesseract_path = tesseract_path
        self._easyocr_reader = None

        if engine == "tesseract" and tesseract_path:
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            except ImportError:
                log.warning("pytesseract not installed")

    def extract_text(self, image: Image.Image) -> str:
        """Extract all text from a PIL image."""
        if self._engine == "tesseract":
            return self._tesseract(image)
        return self._easyocr(image)

    def _tesseract(self, image: Image.Image) -> str:
        try:
            import pytesseract
            text = pytesseract.image_to_string(image, lang="eng")
            return text.strip()
        except Exception as e:
            log.error("Tesseract error: %s — trying easyocr fallback", e)
            return self._easyocr(image)

    def _easyocr(self, image: Image.Image) -> str:
        try:
            import easyocr
            if not self._easyocr_reader:
                log.info("Loading EasyOCR reader (first run may take time)…")
                self._easyocr_reader = easyocr.Reader(["en"], gpu=False)
            import numpy as np
            arr = np.array(image)
            results = self._easyocr_reader.readtext(arr)
            return " ".join(r[1] for r in results).strip()
        except ImportError:
            log.error("Neither tesseract nor easyocr is available")
            return ""
        except Exception as e:
            log.error("EasyOCR error: %s", e)
            return ""
