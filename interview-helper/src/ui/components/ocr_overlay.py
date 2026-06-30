"""Screen region selection overlay for OCR capture."""

from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QScreen, QPixmap
from PySide6.QtWidgets import QWidget, QApplication, QRubberBand


class OCROverlay(QWidget):
    """Full-screen translucent overlay — user drags a rectangle, emits region."""

    region_selected = Signal(int, int, int, int)  # left, top, width, height
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._origin = QPoint()
        self._rubber = QRubberBand(QRubberBand.Shape.Rectangle, self)

    def showFullScreen(self):
        # Expand across all screens
        geo = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geo)
        super().showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._rubber.hide()
            self.hide()
            self.cancelled.emit()

    def mousePressEvent(self, event):
        self._origin = event.pos()
        self._rubber.setGeometry(QRect(self._origin, self._origin))
        self._rubber.show()

    def mouseMoveEvent(self, event):
        self._rubber.setGeometry(QRect(self._origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        rect = QRect(self._origin, event.pos()).normalized()
        self._rubber.hide()
        self.hide()
        if rect.width() > 10 and rect.height() > 10:
            # Convert from widget coords to screen coords
            screen_pos = self.mapToGlobal(rect.topLeft())
            self.region_selected.emit(screen_pos.x(), screen_pos.y(), rect.width(), rect.height())
        else:
            self.cancelled.emit()
