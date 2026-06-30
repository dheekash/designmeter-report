"""Structured application logging."""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "interview_helper", level: str = "INFO", log_file: Path | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    if log_file:
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(fmt)
            logger.addHandler(fh)
        except OSError:
            pass

    return logger


def get_logger(module: str) -> logging.Logger:
    return logging.getLogger(f"interview_helper.{module}")
