"""Dark theme stylesheet for Interview Helper."""

DARK_QSS = """
/* ===== Base ===== */
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: "Segoe UI", "SF Pro Display", system-ui, sans-serif;
    font-size: 13px;
    border: none;
}

/* ===== Main Window ===== */
#MainWindow {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 12px;
}

/* ===== Title Bar ===== */
#TitleBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #161b22, stop:1 #0d1117);
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: 1px solid #21262d;
    padding: 4px 8px;
    min-height: 40px;
}

#AppTitle {
    color: #58a6ff;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

#ProviderLabel {
    color: #8b949e;
    font-size: 11px;
}

/* ===== Status Bar ===== */
#StatusBar {
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 4px 12px;
    min-height: 30px;
}

#StatusIcon {
    font-size: 10px;
}

#StatusText {
    color: #8b949e;
    font-size: 11px;
    font-weight: 500;
}

#CategoryBadge {
    background-color: #1f6feb;
    color: #ffffff;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: none;
    background: #0d1117;
}

QTabBar::tab {
    background: #161b22;
    color: #8b949e;
    padding: 8px 16px;
    border: none;
    font-size: 12px;
    font-weight: 500;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #0d1117;
    color: #58a6ff;
    border-bottom: 2px solid #58a6ff;
}

QTabBar::tab:hover {
    color: #c9d1d9;
    background: #1c2128;
}

/* ===== Transcription Panel ===== */
#TranscriptionPanel {
    background: #0d1117;
    border-bottom: 1px solid #21262d;
    padding: 8px;
}

#TranscriptionLabel {
    color: #8b949e;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

#TranscriptionText {
    color: #e6edf3;
    font-size: 13px;
    line-height: 1.6;
    background: transparent;
    border: none;
    font-style: italic;
    padding: 4px 0;
}

/* ===== Answer Panel ===== */
#AnswerPanel {
    background: #0d1117;
}

#AnswerBrowser {
    background-color: #0d1117;
    color: #c9d1d9;
    font-size: 13px;
    line-height: 1.7;
    border: none;
    padding: 12px;
    selection-background-color: #1f6feb;
}

/* ===== Scrollbar ===== */
QScrollBar:vertical {
    background: #0d1117;
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #58a6ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    height: 6px;
    background: #0d1117;
    border-radius: 3px;
}

QScrollBar::handle:horizontal {
    background: #30363d;
    border-radius: 3px;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #58a6ff;
    color: #58a6ff;
}

QPushButton:pressed {
    background-color: #1f6feb;
    color: #ffffff;
    border-color: #1f6feb;
}

QPushButton#BtnListen {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #238636, stop:1 #1a7f37);
    color: #ffffff;
    border: 1px solid #2ea043;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 8px;
}

QPushButton#BtnListen:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2ea043, stop:1 #238636);
    border-color: #3fb950;
}

QPushButton#BtnStop {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #b91c1c, stop:1 #991b1b);
    color: #ffffff;
    border: 1px solid #dc2626;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 8px;
}

QPushButton#BtnStop:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #dc2626, stop:1 #b91c1c);
}

QPushButton#BtnOCR {
    background-color: #1f3a5f;
    color: #79c0ff;
    border-color: #1f6feb;
}

QPushButton#BtnOCR:hover {
    background-color: #1f6feb;
    color: #ffffff;
}

/* ===== Toolbar ===== */
#ToolBar {
    background: #161b22;
    border-top: 1px solid #21262d;
    padding: 6px 8px;
    min-height: 44px;
}

/* ===== Input Fields ===== */
QLineEdit, QTextEdit {
    background: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #1f6feb;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #58a6ff;
    outline: none;
}

QLineEdit::placeholder {
    color: #484f58;
}

/* ===== History Panel ===== */
#HistoryList {
    background: #161b22;
    border: none;
    outline: none;
}

QListWidget::item {
    background: #161b22;
    color: #c9d1d9;
    padding: 10px 12px;
    border-bottom: 1px solid #21262d;
}

QListWidget::item:selected {
    background: #1c2128;
    color: #58a6ff;
    border-left: 3px solid #58a6ff;
}

QListWidget::item:hover {
    background: #1c2128;
}

/* ===== Combo Box ===== */
QComboBox {
    background: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px 8px;
    min-width: 100px;
}

QComboBox:hover {
    border-color: #58a6ff;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    selection-background-color: #1f6feb;
}

/* ===== Slider (opacity) ===== */
QSlider::groove:horizontal {
    height: 4px;
    background: #30363d;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #58a6ff;
    border: none;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::sub-page:horizontal {
    background: #1f6feb;
    border-radius: 2px;
}

/* ===== Spinner / Progress ===== */
QProgressBar {
    background: #21262d;
    border: none;
    border-radius: 3px;
    height: 4px;
}

QProgressBar::chunk {
    background: #58a6ff;
    border-radius: 3px;
}

/* ===== Tooltip ===== */
QToolTip {
    background: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
}

/* ===== Settings Dialog ===== */
#SettingsDialog QGroupBox {
    border: 1px solid #21262d;
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px;
    color: #8b949e;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

#SettingsDialog QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}

/* ===== Window control buttons ===== */
#BtnMinimize, #BtnClose, #BtnPin {
    background: transparent;
    border: none;
    color: #8b949e;
    font-size: 14px;
    padding: 4px 6px;
    border-radius: 4px;
    min-width: 24px;
    min-height: 24px;
}

#BtnMinimize:hover { background: #21262d; color: #c9d1d9; }
#BtnClose:hover { background: #b91c1c; color: #ffffff; }
#BtnPin:hover { background: #21262d; color: #58a6ff; }

/* ===== Loading indicator ===== */
#LoadingLabel {
    color: #58a6ff;
    font-size: 12px;
    font-weight: 600;
}
"""
