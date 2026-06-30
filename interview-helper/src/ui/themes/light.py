"""Light theme stylesheet."""

LIGHT_QSS = """
QWidget {
    background-color: #f6f8fa;
    color: #24292f;
    font-family: "Segoe UI", "SF Pro Display", system-ui, sans-serif;
    font-size: 13px;
    border: none;
}

#MainWindow {
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 12px;
}

#TitleBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ffffff, stop:1 #f6f8fa);
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: 1px solid #d0d7de;
    padding: 4px 8px;
    min-height: 40px;
}

#AppTitle { color: #0969da; font-size: 14px; font-weight: 700; }
#ProviderLabel { color: #57606a; font-size: 11px; }

#StatusBar {
    background-color: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 4px 12px;
    min-height: 30px;
}

#StatusText { color: #57606a; font-size: 11px; font-weight: 500; }

#CategoryBadge {
    background-color: #0969da;
    color: #ffffff;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
}

QTabBar::tab {
    background: #f6f8fa;
    color: #57606a;
    padding: 8px 16px;
    border: none;
    font-size: 12px;
    font-weight: 500;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #0969da;
    border-bottom: 2px solid #0969da;
}

QTabBar::tab:hover { color: #24292f; }

#TranscriptionText {
    color: #24292f;
    font-size: 13px;
    background: transparent;
    border: none;
    font-style: italic;
    padding: 4px 0;
}

#AnswerBrowser {
    background-color: #ffffff;
    color: #24292f;
    font-size: 13px;
    border: none;
    padding: 12px;
    selection-background-color: #0969da;
    selection-color: #ffffff;
}

QScrollBar:vertical { background: #f6f8fa; width: 6px; border-radius: 3px; }
QScrollBar::handle:vertical { background: #d0d7de; border-radius: 3px; }
QScrollBar::handle:vertical:hover { background: #0969da; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

QPushButton {
    background-color: #f6f8fa;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton:hover { background-color: #e9ecef; border-color: #0969da; color: #0969da; }
QPushButton:pressed { background-color: #0969da; color: #ffffff; border-color: #0969da; }

QPushButton#BtnListen {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2da44e, stop:1 #24943e);
    color: #ffffff; border: 1px solid #2da44e;
    font-weight: 600; padding: 8px 16px; border-radius: 8px;
}

QPushButton#BtnStop {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #cf222e, stop:1 #a40e26);
    color: #ffffff; border: 1px solid #cf222e;
    font-weight: 600; padding: 8px 16px; border-radius: 8px;
}

#ToolBar { background: #ffffff; border-top: 1px solid #d0d7de; padding: 6px 8px; min-height: 44px; }

QLineEdit, QTextEdit {
    background: #ffffff; color: #24292f;
    border: 1px solid #d0d7de; border-radius: 6px; padding: 6px 10px;
}

QLineEdit:focus, QTextEdit:focus { border-color: #0969da; }

QListWidget::item { background: #ffffff; color: #24292f; padding: 10px 12px; border-bottom: 1px solid #d0d7de; }
QListWidget::item:selected { background: #ddf4ff; color: #0969da; border-left: 3px solid #0969da; }
QListWidget::item:hover { background: #f6f8fa; }

QComboBox { background: #f6f8fa; color: #24292f; border: 1px solid #d0d7de; border-radius: 6px; padding: 4px 8px; }
QComboBox:hover { border-color: #0969da; }
QComboBox QAbstractItemView { background: #ffffff; color: #24292f; border: 1px solid #d0d7de; selection-background-color: #0969da; }

QToolTip { background: #ffffff; color: #24292f; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 8px; }

#BtnMinimize, #BtnClose, #BtnPin { background: transparent; border: none; color: #57606a; font-size: 14px; padding: 4px 6px; border-radius: 4px; min-width: 24px; min-height: 24px; }
#BtnMinimize:hover { background: #e9ecef; color: #24292f; }
#BtnClose:hover { background: #cf222e; color: #ffffff; }
#BtnPin:hover { background: #e9ecef; color: #0969da; }

#LoadingLabel { color: #0969da; font-size: 12px; font-weight: 600; }
"""
