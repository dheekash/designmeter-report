"""Answer display panel with live streaming and syntax highlighting."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QPushButton, QLabel, QFrame, QSizePolicy,
)

from .code_highlighter import markdown_to_html


class _StreamWorker(QObject):
    chunk_ready = Signal(str)
    finished = Signal(str, str)  # answer, category
    error = Signal(str)

    def __init__(self, generator, question: str):
        super().__init__()
        self._generator = generator
        self._question = question

    def run(self):
        try:
            chunks: list[str] = []
            result = self._generator.generate(
                self._question,
                on_chunk=lambda c: (chunks.append(c), self.chunk_ready.emit(c)),
            )
            self.finished.emit(result["answer"], result["category"])
        except Exception as e:
            self.error.emit(str(e))


class AnswerWidget(QWidget):
    """Scrollable panel that streams and renders AI answers."""

    copy_requested = Signal(str)
    save_requested = Signal(str, str)  # answer, category

    def __init__(self, dark: bool = True, parent=None):
        super().__init__(parent)
        self._dark = dark
        self._current_answer = ""
        self._current_category = ""
        self._stream_buffer = ""
        self._thread: QThread | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- header row
        header = QWidget()
        header.setFixedHeight(36)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 0, 8, 0)

        self._category_badge = QLabel("Waiting…")
        self._category_badge.setObjectName("CategoryBadge")

        self._loading_label = QLabel("● Processing…")
        self._loading_label.setObjectName("LoadingLabel")
        self._loading_label.hide()

        hl.addWidget(self._category_badge)
        hl.addStretch()
        hl.addWidget(self._loading_label)
        layout.addWidget(header)

        # --- browser
        self._browser = QTextBrowser()
        self._browser.setObjectName("AnswerBrowser")
        self._browser.setOpenExternalLinks(False)
        self._browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._browser, stretch=1)

        # --- action toolbar
        toolbar = QWidget()
        toolbar.setObjectName("ToolBar")
        toolbar.setFixedHeight(44)
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(8, 4, 8, 4)
        tl.setSpacing(6)

        self._btn_copy = QPushButton("📋 Copy")
        self._btn_copy.setToolTip("Copy answer to clipboard (Ctrl+Shift+C)")
        self._btn_copy.clicked.connect(self._copy)

        self._btn_save = QPushButton("⭐ Save")
        self._btn_save.setToolTip("Save to history")
        self._btn_save.clicked.connect(self._save)

        self._btn_clear = QPushButton("🗑 Clear")
        self._btn_clear.clicked.connect(self.clear)

        tl.addWidget(self._btn_copy)
        tl.addWidget(self._btn_save)
        tl.addStretch()
        tl.addWidget(self._btn_clear)
        layout.addWidget(toolbar)

    # ------------------------------------------------------------------

    def stream_answer(self, question: str, generator) -> None:
        """Start streaming an answer for the given question."""
        self._stream_buffer = ""
        self._current_answer = ""
        self._loading_label.show()
        self._browser.setHtml(self._welcome_html("Generating answer…"))

        worker = _StreamWorker(generator, question)
        thread = QThread(self)
        worker.moveToThread(thread)

        worker.chunk_ready.connect(self._on_chunk)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        self._thread = thread
        thread.start()

    def _on_chunk(self, chunk: str) -> None:
        self._stream_buffer += chunk
        html = markdown_to_html(self._stream_buffer, self._dark)
        self._browser.setHtml(html)
        self._browser.moveCursor(QTextCursor.MoveOperation.End)

    def _on_finished(self, answer: str, category: str) -> None:
        self._current_answer = answer
        self._current_category = category
        self._category_badge.setText(f"  {category}  ")
        self._loading_label.hide()
        html = markdown_to_html(answer, self._dark)
        self._browser.setHtml(html)

    def _on_error(self, error: str) -> None:
        self._loading_label.hide()
        self._browser.setHtml(self._welcome_html(f"⚠️ Error: {error}"))

    def _copy(self) -> None:
        if self._current_answer:
            try:
                import pyperclip
                pyperclip.copy(self._current_answer)
            except Exception:
                from PySide6.QtWidgets import QApplication
                QApplication.clipboard().setText(self._current_answer)
            self.copy_requested.emit(self._current_answer)

    def _save(self) -> None:
        if self._current_answer:
            self.save_requested.emit(self._current_answer, self._current_category)

    def clear(self) -> None:
        self._current_answer = ""
        self._stream_buffer = ""
        self._category_badge.setText("Waiting…")
        self._browser.setHtml(self._welcome_html())

    def set_dark(self, dark: bool) -> None:
        self._dark = dark
        if self._current_answer:
            self._browser.setHtml(markdown_to_html(self._current_answer, dark))
        else:
            self._browser.setHtml(self._welcome_html())

    def _welcome_html(self, msg: str = "") -> str:
        bg = "#0d1117" if self._dark else "#ffffff"
        fg = "#8b949e" if self._dark else "#57606a"
        accent = "#58a6ff" if self._dark else "#0969da"
        content = msg or (
            "🎙 Start listening or type a question below.<br><br>"
            "Interview Helper will automatically detect the category and generate<br>"
            "a comprehensive, interview-ready answer."
        )
        return f"""<!DOCTYPE html><html><head><style>
            body {{ background:{bg}; color:{fg}; font-family:'Segoe UI',sans-serif;
                    font-size:13px; display:flex; align-items:center;
                    justify-content:center; min-height:200px; text-align:center;
                    line-height:1.6; padding:24px; }}
            .accent {{ color:{accent}; font-size:28px; display:block; margin-bottom:12px; }}
        </style></head><body>
        <div><span class="accent">✦</span>{content}</div>
        </body></html>"""
