"""Interview Helper — Main floating window."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Optional

from PySide6.QtCore import (
    Qt, QPoint, QTimer, Signal, Slot, QThread, QObject,
)
from PySide6.QtGui import (
    QFont, QIcon, QKeySequence, QShortcut, QAction,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTabWidget, QTextEdit,
    QSlider, QComboBox, QSizePolicy, QFrame, QSystemTrayIcon,
    QMenu, QToolButton, QSplitter,
)

from .themes import DARK_QSS, LIGHT_QSS
from .components.answer_widget import AnswerWidget
from .components.history_widget import HistoryWidget
from .components.settings_dialog import SettingsDialog
from .components.ocr_overlay import OCROverlay
from ..utils.logger import get_logger
from ..ai.detector import detect_category

log = get_logger("ui.main_window")

# Status states
_STATUS = {
    "ready":      ("🟢", "Ready"),
    "listening":  ("🔴", "Listening…"),
    "processing": ("🟡", "Processing…"),
    "thinking":   ("🔵", "Thinking…"),
    "offline":    ("⚫", "Offline"),
    "loading":    ("⚪", "Loading model…"),
}


class MainWindow(QMainWindow):
    """Frameless floating assistant window."""

    # Signals emitted from background threads → processed on main thread
    _transcript_received = Signal(str)
    _status_changed = Signal(str)
    _question_text_signal = Signal(str)

    def __init__(self, app_core):
        super().__init__()
        self._core = app_core
        self._drag_pos: Optional[QPoint] = None
        self._dark = app_core.settings.default_theme == "dark"
        self._pinned = True
        self._compact = False

        self._setup_window()
        self._setup_ui()
        self._apply_theme()
        self._setup_shortcuts()
        self._setup_tray()

        # Wire signals
        self._transcript_received.connect(self._on_transcript)
        self._status_changed.connect(self._on_status_changed)
        self._question_text_signal.connect(self._on_question_submitted)

        # Notify core so it can emit signals back to us
        self._core.set_ui_callbacks(
            on_transcript=lambda t: self._transcript_received.emit(t),
            on_status=lambda s: self._status_changed.emit(s),
        )

    # ------------------------------------------------------------------ #
    #  Window setup                                                        #
    # ------------------------------------------------------------------ #

    def _setup_window(self):
        self.setWindowTitle("Interview Helper")
        self.setObjectName("MainWindow")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        s = self._core.settings
        self.resize(s.window_width, s.window_height)
        self.setWindowOpacity(s.default_opacity)

        # Restore last position
        self._move_to_default()

    def _move_to_default(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 20, screen.top() + 40)

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("MainWindow")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_title_bar())
        root.addWidget(self._build_status_bar())
        root.addWidget(self._build_input_row())

        tabs = QTabWidget()
        tabs.setObjectName("Tabs")
        tabs.addTab(self._build_answer_tab(), "💡 Answer")
        tabs.addTab(self._build_history_tab(), "📚 History")
        root.addWidget(tabs, stretch=1)

    # --- Title Bar ---------------------------------------------------

    def _build_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("TitleBar")
        bar.setFixedHeight(42)
        bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        hl = QHBoxLayout(bar)
        hl.setContentsMargins(12, 0, 8, 0)
        hl.setSpacing(8)

        icon_label = QLabel("✦")
        icon_label.setStyleSheet("font-size:16px; color:#58a6ff;")

        title = QLabel("Interview Helper")
        title.setObjectName("AppTitle")

        self._provider_label = QLabel(f"[{self._core.settings.active_provider()}]")
        self._provider_label.setObjectName("ProviderLabel")

        hl.addWidget(icon_label)
        hl.addWidget(title)
        hl.addWidget(self._provider_label)
        hl.addStretch()

        # Opacity slider (compact)
        opc_label = QLabel("Opacity:")
        opc_label.setStyleSheet("color:#484f58; font-size:10px;")
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(20, 100)
        self._opacity_slider.setValue(int(self._core.settings.default_opacity * 100))
        self._opacity_slider.setFixedWidth(70)
        self._opacity_slider.valueChanged.connect(
            lambda v: self.setWindowOpacity(v / 100.0)
        )

        hl.addWidget(opc_label)
        hl.addWidget(self._opacity_slider)

        # Window controls
        self._btn_pin = QPushButton("📌")
        self._btn_pin.setObjectName("BtnPin")
        self._btn_pin.setToolTip("Toggle always-on-top (Ctrl+Shift+P)")
        self._btn_pin.setFixedSize(28, 28)
        self._btn_pin.clicked.connect(self._toggle_pin)

        self._btn_theme = QPushButton("🌙")
        self._btn_theme.setObjectName("BtnPin")
        self._btn_theme.setToolTip("Toggle Dark/Light theme")
        self._btn_theme.setFixedSize(28, 28)
        self._btn_theme.clicked.connect(self._toggle_theme)

        btn_settings = QPushButton("⚙")
        btn_settings.setObjectName("BtnPin")
        btn_settings.setToolTip("Settings")
        btn_settings.setFixedSize(28, 28)
        btn_settings.clicked.connect(self._open_settings)

        btn_minimize = QPushButton("—")
        btn_minimize.setObjectName("BtnMinimize")
        btn_minimize.setFixedSize(28, 28)
        btn_minimize.clicked.connect(self.showMinimized)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("BtnClose")
        btn_close.setFixedSize(28, 28)
        btn_close.clicked.connect(self._on_close)

        for w in (self._btn_pin, self._btn_theme, btn_settings, btn_minimize, btn_close):
            hl.addWidget(w)

        # Make title bar draggable
        bar.mousePressEvent = self._title_mouse_press
        bar.mouseMoveEvent = self._title_mouse_move
        bar.mouseReleaseEvent = self._title_mouse_release

        return bar

    # --- Status Bar ---------------------------------------------------

    def _build_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("StatusBar")
        bar.setFixedHeight(32)

        hl = QHBoxLayout(bar)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(8)

        self._status_icon = QLabel("🟢")
        self._status_icon.setObjectName("StatusIcon")

        self._status_text = QLabel("Ready")
        self._status_text.setObjectName("StatusText")

        self._model_badge = QLabel("")
        self._model_badge.setObjectName("CategoryBadge")
        self._model_badge.hide()

        hl.addWidget(self._status_icon)
        hl.addWidget(self._status_text)
        hl.addStretch()
        hl.addWidget(self._model_badge)

        return bar

    # --- Input Row ----------------------------------------------------

    def _build_input_row(self) -> QWidget:
        row = QWidget()
        row.setFixedHeight(52)
        hl = QHBoxLayout(row)
        hl.setContentsMargins(8, 4, 8, 4)
        hl.setSpacing(6)

        self._question_input = QLineEdit()
        self._question_input.setPlaceholderText("Type a question or paste code…")
        self._question_input.returnPressed.connect(self._on_manual_question)
        hl.addWidget(self._question_input, stretch=1)

        self._btn_listen = QPushButton("🎙 Listen")
        self._btn_listen.setObjectName("BtnListen")
        self._btn_listen.setFixedWidth(90)
        self._btn_listen.clicked.connect(self._toggle_listen)

        self._btn_stop = QPushButton("⏹ Stop")
        self._btn_stop.setObjectName("BtnStop")
        self._btn_stop.setFixedWidth(80)
        self._btn_stop.clicked.connect(self._stop_listen)
        self._btn_stop.hide()

        self._btn_ocr = QPushButton("📸 OCR")
        self._btn_ocr.setObjectName("BtnOCR")
        self._btn_ocr.setFixedWidth(80)
        self._btn_ocr.setToolTip("Capture screen region (Ctrl+Shift+O)")
        self._btn_ocr.clicked.connect(self._start_ocr)

        hl.addWidget(self._btn_listen)
        hl.addWidget(self._btn_stop)
        hl.addWidget(self._btn_ocr)

        return row

    # --- Answer Tab ---------------------------------------------------

    def _build_answer_tab(self) -> QWidget:
        tab = QWidget()
        vl = QVBoxLayout(tab)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        # Transcription display (collapsible)
        self._transcript_frame = QFrame()
        self._transcript_frame.setFixedHeight(60)
        self._transcript_frame.setStyleSheet("background: transparent; border-bottom: 1px solid #21262d;")
        tf_layout = QVBoxLayout(self._transcript_frame)
        tf_layout.setContentsMargins(12, 4, 12, 4)

        lbl = QLabel("LIVE TRANSCRIPTION")
        lbl.setObjectName("TranscriptionLabel")
        lbl.setStyleSheet("color:#484f58; font-size:10px; font-weight:600; letter-spacing:1px;")

        self._transcript_label = QLabel("—")
        self._transcript_label.setObjectName("TranscriptionText")
        self._transcript_label.setWordWrap(True)
        self._transcript_label.setStyleSheet("color:#8b949e; font-style:italic; font-size:12px;")

        tf_layout.addWidget(lbl)
        tf_layout.addWidget(self._transcript_label)
        vl.addWidget(self._transcript_frame)

        # Answer panel
        self._answer_widget = AnswerWidget(dark=self._dark, parent=self)
        self._answer_widget.save_requested.connect(self._save_to_history)
        vl.addWidget(self._answer_widget, stretch=1)

        return tab

    # --- History Tab --------------------------------------------------

    def _build_history_tab(self) -> QWidget:
        self._history_widget = HistoryWidget(
            repository=self._core.repository,
            dark=self._dark,
            parent=self,
        )
        self._history_widget.item_selected.connect(self._load_history_item)
        return self._history_widget

    # ------------------------------------------------------------------ #
    #  Theme & appearance                                                  #
    # ------------------------------------------------------------------ #

    def _apply_theme(self):
        self.setStyleSheet(DARK_QSS if self._dark else LIGHT_QSS)
        self._answer_widget.set_dark(self._dark)
        self._btn_theme.setText("☀️" if self._dark else "🌙")

    def _toggle_theme(self):
        self._dark = not self._dark
        self._apply_theme()

    # ------------------------------------------------------------------ #
    #  Always-on-top / pin                                                #
    # ------------------------------------------------------------------ #

    def _toggle_pin(self):
        self._pinned = not self._pinned
        flags = self.windowFlags()
        if self._pinned:
            flags |= Qt.WindowType.WindowStaysOnTopHint
            self._btn_pin.setText("📌")
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            self._btn_pin.setText("📍")
        self.setWindowFlags(flags)
        self.show()

    # ------------------------------------------------------------------ #
    #  Listen / stop                                                       #
    # ------------------------------------------------------------------ #

    def _toggle_listen(self):
        if self._core.is_listening:
            self._stop_listen()
        else:
            self._start_listen()

    def _start_listen(self):
        self._core.start_listening()
        self._btn_listen.hide()
        self._btn_stop.show()
        self._set_status("listening")

    def _stop_listen(self):
        self._core.stop_listening()
        self._btn_stop.hide()
        self._btn_listen.show()
        self._set_status("ready")

    # ------------------------------------------------------------------ #
    #  OCR                                                                 #
    # ------------------------------------------------------------------ #

    def _start_ocr(self):
        self._ocr_overlay = OCROverlay()
        self._ocr_overlay.region_selected.connect(self._on_ocr_region)
        self._ocr_overlay.cancelled.connect(lambda: None)
        self.hide()
        QTimer.singleShot(200, self._ocr_overlay.showFullScreen)

    def _on_ocr_region(self, left: int, top: int, width: int, height: int):
        self.show()
        self._set_status("processing")
        self._transcript_label.setText("📸 Extracting text from screenshot…")

        def _run():
            try:
                from ..ocr.capture import capture_region
                img = capture_region((left, top, width, height))
                if img:
                    text = self._core.ocr_engine.extract_text(img)
                    if text.strip():
                        self._question_text_signal.emit(text.strip())
                    else:
                        self._status_changed.emit("ready")
                        self._transcript_received.emit("⚠️ No text found in screenshot")
            except Exception as e:
                log.error("OCR error: %s", e)
                self._status_changed.emit("ready")

        threading.Thread(target=_run, daemon=True).start()

    # ------------------------------------------------------------------ #
    #  Manual question input                                               #
    # ------------------------------------------------------------------ #

    def _on_manual_question(self):
        text = self._question_input.text().strip()
        if text:
            self._question_input.clear()
            self._on_question_submitted(text)

    @Slot(str)
    def _on_question_submitted(self, question: str):
        cat = detect_category(question)
        self._transcript_label.setText(f'"{question[:100]}…"' if len(question) > 100 else f'"{question}"')
        self._model_badge.setText(f"  {cat}  ")
        self._model_badge.show()
        self._set_status("thinking")
        self._answer_widget.stream_answer(question, self._core.generator)

    # ------------------------------------------------------------------ #
    #  Signals from core                                                   #
    # ------------------------------------------------------------------ #

    @Slot(str)
    def _on_transcript(self, text: str):
        self._transcript_label.setText(text)
        # If transcript looks like a complete question, trigger answer generation
        if len(text.split()) >= 4 and any(text.endswith(c) for c in "?.,!"):
            self._on_question_submitted(text)

    @Slot(str)
    def _on_status_changed(self, state: str):
        self._set_status(state)

    def _set_status(self, state: str):
        icon, text = _STATUS.get(state, ("⚪", state))
        self._status_icon.setText(icon)
        self._status_text.setText(text)

    # ------------------------------------------------------------------ #
    #  History                                                             #
    # ------------------------------------------------------------------ #

    def _save_to_history(self, answer: str, category: str):
        question = self._transcript_label.text().strip('"')
        if question and answer:
            self._core.repository.save(question, category, answer, self._core.generator._provider.name)
            self._history_widget.refresh()

    def _load_history_item(self, record: dict):
        from .components.code_highlighter import markdown_to_html
        self._answer_widget._browser.setHtml(
            markdown_to_html(record.get("answer", ""), self._dark)
        )
        self._answer_widget._current_answer = record.get("answer", "")
        self._answer_widget._current_category = record.get("category", "")
        self._answer_widget._category_badge.setText(f"  {record.get('category','')}  ")
        self._transcript_label.setText(record.get("question", ""))

    # ------------------------------------------------------------------ #
    #  Settings                                                            #
    # ------------------------------------------------------------------ #

    def _open_settings(self):
        dlg = SettingsDialog(self._core.settings, self)
        dlg.settings_changed.connect(self._apply_settings)
        dlg.exec()

    def _apply_settings(self, data: dict):
        s = self._core.settings
        for k, v in data.items():
            if hasattr(s, k):
                setattr(s, k, v)
        self._dark = s.default_theme == "dark"
        self._apply_theme()
        self.setWindowOpacity(s.default_opacity)
        self._opacity_slider.setValue(int(s.default_opacity * 100))
        self._core.rebuild_provider()
        self._provider_label.setText(f"[{s.active_provider()}]")

    # ------------------------------------------------------------------ #
    #  Shortcuts                                                           #
    # ------------------------------------------------------------------ #

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(self._start_listen)
        QShortcut(QKeySequence("Ctrl+Shift+X"), self).activated.connect(self._stop_listen)
        QShortcut(QKeySequence("Ctrl+Shift+H"), self).activated.connect(self._toggle_visibility)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self._answer_widget._copy)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self).activated.connect(self._start_ocr)
        QShortcut(QKeySequence("Ctrl+Shift+P"), self).activated.connect(self._toggle_pin)
        QShortcut(QKeySequence("Ctrl+Shift+L"), self).activated.connect(self._answer_widget.clear)

    def _toggle_visibility(self):
        self.hide() if self.isVisible() else self.show()

    # ------------------------------------------------------------------ #
    #  System tray                                                         #
    # ------------------------------------------------------------------ #

    def _setup_tray(self):
        self._tray = QSystemTrayIcon(self)
        self._tray.setToolTip("Interview Helper")

        menu = QMenu()
        menu.addAction("Show/Hide", self._toggle_visibility)
        menu.addAction("Start Listening", self._start_listen)
        menu.addAction("Stop Listening", self._stop_listen)
        menu.addSeparator()
        menu.addAction("Settings", self._open_settings)
        menu.addAction("Quit", self._on_close)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(lambda r: self._toggle_visibility() if r == QSystemTrayIcon.ActivationReason.Trigger else None)
        self._tray.show()

    # ------------------------------------------------------------------ #
    #  Drag support (frameless window)                                     #
    # ------------------------------------------------------------------ #

    def _title_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def _title_mouse_release(self, event):
        self._drag_pos = None

    # ------------------------------------------------------------------ #
    #  Close                                                               #
    # ------------------------------------------------------------------ #

    def _on_close(self):
        self._core.shutdown()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()  # minimize to tray instead
