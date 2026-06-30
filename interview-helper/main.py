#!/usr/bin/env python3
"""
Interview Helper — Real-time AI interview assistant
Entry point: python main.py
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from src.app import AppCore
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger


def main():
    # High-DPI support
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Interview Helper")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("InterviewHelper")

    # Default font
    font = QFont("Segoe UI", 12)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Don't quit when last window is hidden (stays in tray)
    app.setQuitOnLastWindowClosed(False)

    # Core
    core = AppCore()

    # Main window
    window = MainWindow(app_core=core)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
