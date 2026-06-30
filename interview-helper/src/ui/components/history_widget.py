"""History panel — search, filter, browse past Q&A pairs."""

from __future__ import annotations

from typing import Callable, List, Optional

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QFileDialog,
    QAbstractItemView, QFrame,
)

from ..components.code_highlighter import markdown_to_html


class HistoryWidget(QWidget):
    """Full history browser with search, filter, and export."""

    item_selected = Signal(dict)  # emitted when user clicks a record

    def __init__(self, repository, dark: bool = True, parent=None):
        super().__init__(parent)
        self._repo = repository
        self._dark = dark
        self._records: List[dict] = []
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._do_search)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # --- search bar
        search_row = QHBoxLayout()
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("🔍  Search questions & answers…")
        self._search_box.textChanged.connect(lambda: self._search_timer.start())
        search_row.addWidget(self._search_box, stretch=1)
        layout.addLayout(search_row)

        # --- filter row
        filter_row = QHBoxLayout()

        self._cat_combo = QComboBox()
        self._cat_combo.addItem("All Categories")
        self._cat_combo.currentIndexChanged.connect(self._do_search)
        filter_row.addWidget(self._cat_combo)

        self._fav_check = QCheckBox("Favorites only")
        self._fav_check.stateChanged.connect(self._do_search)
        filter_row.addWidget(self._fav_check)

        filter_row.addStretch()

        self._count_label = QLabel("0 records")
        self._count_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        filter_row.addWidget(self._count_label)

        layout.addLayout(filter_row)

        # --- list
        self._list = QListWidget()
        self._list.setObjectName("HistoryList")
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.itemClicked.connect(self._on_item_click)
        layout.addWidget(self._list, stretch=1)

        # --- action bar
        action_row = QHBoxLayout()
        self._btn_refresh = QPushButton("↻ Refresh")
        self._btn_refresh.clicked.connect(self.refresh)

        self._btn_export = QPushButton("📤 Export")
        self._btn_export.clicked.connect(self._export)

        self._btn_delete = QPushButton("🗑 Delete")
        self._btn_delete.clicked.connect(self._delete_selected)

        action_row.addWidget(self._btn_refresh)
        action_row.addWidget(self._btn_export)
        action_row.addStretch()
        action_row.addWidget(self._btn_delete)
        layout.addLayout(action_row)

    def refresh(self) -> None:
        # Update category filter
        categories = self._repo.all_categories()
        current = self._cat_combo.currentText()
        self._cat_combo.blockSignals(True)
        self._cat_combo.clear()
        self._cat_combo.addItem("All Categories")
        for c in categories:
            self._cat_combo.addItem(c)
        idx = self._cat_combo.findText(current)
        if idx >= 0:
            self._cat_combo.setCurrentIndex(idx)
        self._cat_combo.blockSignals(False)
        self._do_search()

    def _do_search(self) -> None:
        query = self._search_box.text()
        cat_text = self._cat_combo.currentText()
        category = None if cat_text == "All Categories" else cat_text
        favorites = self._fav_check.isChecked()

        self._records = self._repo.search(query=query, category=category, favorites_only=favorites)
        self._populate_list()

    def _populate_list(self) -> None:
        self._list.clear()
        for r in self._records:
            q = r.get("question", "")[:80]
            cat = r.get("category", "")
            ts = str(r.get("created_at", ""))[:16]
            fav = "⭐ " if r.get("is_favorite") else ""
            text = f"{fav}[{cat}] {q}\n{ts}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, r)
            self._list.addItem(item)
        self._count_label.setText(f"{len(self._records)} records")

    def _on_item_click(self, item: QListWidgetItem) -> None:
        record = item.data(Qt.ItemDataRole.UserRole)
        if record:
            self.item_selected.emit(record)

    def _delete_selected(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        record = item.data(Qt.ItemDataRole.UserRole)
        if record and self._repo.delete(record["id"]):
            self.refresh()

    def _export(self) -> None:
        from pathlib import Path
        from ...utils.exporter import to_markdown, to_html, to_json, to_pdf

        path, fmt = QFileDialog.getSaveFileName(
            self, "Export History", str(Path.home() / "interview_history"),
            "Markdown (*.md);;HTML (*.html);;JSON (*.json);;PDF (*.pdf)"
        )
        if not path:
            return

        records = self._records or self._repo.recent(500)
        p = Path(path)
        if path.endswith(".md"):
            to_markdown(records, p)
        elif path.endswith(".html"):
            to_html(records, p)
        elif path.endswith(".json"):
            to_json(records, p)
        elif path.endswith(".pdf"):
            to_pdf(records, p)
