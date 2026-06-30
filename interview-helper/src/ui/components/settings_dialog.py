"""Settings dialog."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSlider, QLabel, QPushButton,
    QGroupBox, QCheckBox, QFileDialog, QTabWidget, QWidget,
)


class SettingsDialog(QDialog):
    settings_changed = Signal(dict)

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Settings — Interview Helper")
        self.setObjectName("SettingsDialog")
        self.setMinimumWidth(480)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # ---- AI Tab ----
        ai_tab = QWidget()
        ai_form = QFormLayout(ai_tab)
        ai_form.setContentsMargins(12, 12, 12, 12)
        ai_form.setSpacing(10)

        self._provider_combo = QComboBox()
        self._provider_combo.addItems(["openai", "claude", "gemini", "ollama"])
        self._provider_combo.setCurrentText(self._settings.ai_provider)
        ai_form.addRow("Primary Provider:", self._provider_combo)

        self._openai_key = QLineEdit(self._settings.openai_api_key)
        self._openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._openai_key.setPlaceholderText("sk-...")
        ai_form.addRow("OpenAI API Key:", self._openai_key)

        self._openai_model = QLineEdit(self._settings.openai_model)
        ai_form.addRow("OpenAI Model:", self._openai_model)

        self._claude_key = QLineEdit(self._settings.anthropic_api_key)
        self._claude_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._claude_key.setPlaceholderText("sk-ant-...")
        ai_form.addRow("Claude API Key:", self._claude_key)

        self._claude_model = QLineEdit(self._settings.claude_model)
        ai_form.addRow("Claude Model:", self._claude_model)

        self._gemini_key = QLineEdit(self._settings.gemini_api_key)
        self._gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        ai_form.addRow("Gemini API Key:", self._gemini_key)

        self._ollama_url = QLineEdit(self._settings.ollama_base_url)
        ai_form.addRow("Ollama URL:", self._ollama_url)

        self._ollama_model = QLineEdit(self._settings.ollama_model)
        ai_form.addRow("Ollama Model:", self._ollama_model)

        tabs.addTab(ai_tab, "🤖 AI")

        # ---- Audio Tab ----
        audio_tab = QWidget()
        audio_form = QFormLayout(audio_tab)
        audio_form.setContentsMargins(12, 12, 12, 12)
        audio_form.setSpacing(10)

        self._whisper_model = QComboBox()
        self._whisper_model.addItems(["tiny", "base", "small", "medium", "large-v3"])
        self._whisper_model.setCurrentText(self._settings.whisper_model)
        audio_form.addRow("Whisper Model:", self._whisper_model)

        self._whisper_device = QComboBox()
        self._whisper_device.addItems(["cpu", "cuda"])
        self._whisper_device.setCurrentText(self._settings.whisper_device)
        audio_form.addRow("Device:", self._whisper_device)

        self._whisper_lang = QLineEdit(self._settings.whisper_language or "")
        self._whisper_lang.setPlaceholderText("en (leave blank for auto)")
        audio_form.addRow("Language:", self._whisper_lang)

        tabs.addTab(audio_tab, "🎙 Audio")

        # ---- UI Tab ----
        ui_tab = QWidget()
        ui_form = QFormLayout(ui_tab)
        ui_form.setContentsMargins(12, 12, 12, 12)
        ui_form.setSpacing(10)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["dark", "light"])
        self._theme_combo.setCurrentText(self._settings.default_theme)
        ui_form.addRow("Theme:", self._theme_combo)

        opacity_row = QHBoxLayout()
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(30, 100)
        self._opacity_slider.setValue(int(self._settings.default_opacity * 100))
        self._opacity_label = QLabel(f"{int(self._settings.default_opacity * 100)}%")
        self._opacity_slider.valueChanged.connect(
            lambda v: self._opacity_label.setText(f"{v}%")
        )
        opacity_row.addWidget(self._opacity_slider)
        opacity_row.addWidget(self._opacity_label)
        ui_form.addRow("Opacity:", opacity_row)

        self._resume_path = QLineEdit(self._settings.resume_path or "")
        self._resume_path.setPlaceholderText("Path to your resume PDF or TXT…")
        resume_btn = QPushButton("Browse…")
        resume_btn.clicked.connect(self._browse_resume)
        resume_row = QHBoxLayout()
        resume_row.addWidget(self._resume_path)
        resume_row.addWidget(resume_btn)
        ui_form.addRow("Resume File:", resume_row)

        tabs.addTab(ui_tab, "🎨 UI")

        layout.addWidget(tabs)

        # ---- Buttons ----
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _browse_resume(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Resume", "", "PDF (*.pdf);;Text (*.txt);;All (*)")
        if path:
            self._resume_path.setText(path)

    def _save(self):
        data = {
            "ai_provider": self._provider_combo.currentText(),
            "openai_api_key": self._openai_key.text(),
            "openai_model": self._openai_model.text(),
            "anthropic_api_key": self._claude_key.text(),
            "claude_model": self._claude_model.text(),
            "gemini_api_key": self._gemini_key.text(),
            "ollama_base_url": self._ollama_url.text(),
            "ollama_model": self._ollama_model.text(),
            "whisper_model": self._whisper_model.currentText(),
            "whisper_device": self._whisper_device.currentText(),
            "whisper_language": self._whisper_lang.text() or None,
            "default_theme": self._theme_combo.currentText(),
            "default_opacity": self._opacity_slider.value() / 100.0,
            "resume_path": self._resume_path.text() or None,
        }
        self.settings_changed.emit(data)
        self.accept()
