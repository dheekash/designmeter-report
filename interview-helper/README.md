# ✦ Interview Helper

**Real-time AI interview assistant for technical, coding, and data engineering interviews.**

A modern floating desktop application that stays on top during online interviews (Teams, Zoom, Meet, Webex) and provides instant AI-generated answers for SQL, PySpark, Python, DSA, System Design, Behavioral, and 20+ other categories — all within 2–3 seconds.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🎙 **Live Speech Recognition** | faster-whisper (tiny → large-v3), accent-aware, silence detection |
| 🤖 **Multi-provider AI** | OpenAI GPT-4o · Claude Sonnet · Gemini 1.5 Pro · Ollama (offline) |
| 🔍 **Auto Category Detection** | 25 categories — SQL, PySpark, DSA, System Design, Behavioral… |
| 💡 **Structured Answers** | Short answer · Deep dive · Code · Complexity · Edge cases · Follow-ups |
| 📸 **OCR Capture** | Select any screen region → extract text → get answer |
| 📚 **History & Search** | SQLite · search · filter by category · favorites · export |
| 📤 **Export** | Markdown · HTML · JSON · PDF |
| 🎨 **Premium UI** | Dark/Light themes · transparency · always-on-top · draggable · resizable |
| ⌨️ **Global Hotkeys** | Ctrl+Shift+S/X/H/C/O/P/L |
| 📌 **System Tray** | Minimizes to tray; accessible from anywhere |

---

## 🚀 Quick Start

### 1. Install

```bash
# Windows — double-click install.bat
# Or manually:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
copy .env.example .env
# Edit .env — add at least one API key
```

Minimum `.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
WHISPER_MODEL=base
```

### 3. Run

```bash
# Windows
run.bat
# Or:
python main.py
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+S` | Start listening |
| `Ctrl+Shift+X` | Stop listening |
| `Ctrl+Shift+H` | Hide / Show window |
| `Ctrl+Shift+C` | Copy answer to clipboard |
| `Ctrl+Shift+O` | OCR screen capture |
| `Ctrl+Shift+P` | Pin / Unpin always-on-top |
| `Ctrl+Shift+L` | Clear answer panel |

---

## 🤖 AI Providers

| Provider | Model | Key Env Var | Notes |
|----------|-------|-------------|-------|
| **OpenAI** | `gpt-4o` | `OPENAI_API_KEY` | Fastest, best coding |
| **Claude** | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` | Best explanations |
| **Gemini** | `gemini-1.5-pro` | `GEMINI_API_KEY` | Good for data questions |
| **Ollama** | `llama3.1` | *(none)* | Fully offline |

Set `AI_PROVIDER=openai|claude|gemini|ollama` in `.env`. The app falls back to the next available provider automatically.

---

## 🎙 Speech Recognition

```env
WHISPER_MODEL=base     # tiny|base|small|medium|large-v3
WHISPER_DEVICE=cpu     # cpu|cuda
WHISPER_LANGUAGE=en    # leave blank for auto-detect
AUDIO_PAUSE_DURATION=1.5   # seconds of silence before sending chunk
```

**Model size guide:**
- `tiny` — fastest, lower accuracy (~39 MB)
- `base` — good balance (**recommended**, ~74 MB)
- `small` — better accuracy (~244 MB)
- `medium` — high accuracy (~769 MB)
- `large-v3` — best accuracy, slower (~1550 MB)

---

## 📸 OCR Setup

### Tesseract (recommended):
1. Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Set path in `.env`:
```env
TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe
```

---

## 📂 Project Structure

```
interview-helper/
├── main.py                  # Entry point
├── requirements.txt
├── .env.example             # Config template
├── install.bat              # Windows installer
├── run.bat                  # Quick launch
├── build_exe.py             # PyInstaller build
├── src/
│   ├── app.py               # AppCore — wires all services
│   ├── config/
│   │   └── settings.py      # Environment-based settings
│   ├── ui/
│   │   ├── main_window.py   # Floating window
│   │   ├── components/
│   │   │   ├── answer_widget.py     # AI answer display + streaming
│   │   │   ├── history_widget.py    # Q&A history browser
│   │   │   ├── settings_dialog.py   # Settings UI
│   │   │   ├── ocr_overlay.py       # Screen capture overlay
│   │   │   └── code_highlighter.py  # Markdown → HTML with Pygments
│   │   └── themes/
│   │       ├── dark.py      # Dark theme QSS
│   │       └── light.py     # Light theme QSS
│   ├── audio/
│   │   ├── recorder.py      # Microphone capture
│   │   └── transcriber.py   # faster-whisper STT
│   ├── ai/
│   │   ├── base.py          # Abstract provider
│   │   ├── detector.py      # Question category detection
│   │   ├── generator.py     # Answer generation + prompts
│   │   └── providers/
│   │       ├── openai_provider.py
│   │       ├── claude_provider.py
│   │       ├── gemini_provider.py
│   │       └── ollama_provider.py
│   ├── ocr/
│   │   ├── capture.py       # mss screen capture
│   │   └── engine.py        # Tesseract / EasyOCR
│   ├── database/
│   │   ├── models.py        # SQLAlchemy ORM
│   │   └── repository.py    # CRUD operations
│   ├── hotkeys/
│   │   └── manager.py       # Global hotkey registration
│   └── utils/
│       ├── cache.py         # LRU response cache
│       ├── exporter.py      # MD/HTML/JSON/PDF export
│       └── logger.py        # Structured logging
└── tests/
    ├── test_detector.py
    └── test_cache.py
```

---

## 🏗 Build Executable

```bash
pip install pyinstaller
python build_exe.py
# Output: dist/InterviewHelper.exe
```

---

## 🔌 Adding a New AI Provider

1. Create `src/ai/providers/my_provider.py` implementing `AIProvider`
2. Register in `src/ai/__init__.py` → `build_provider()`
3. Add settings fields in `src/config/settings.py`
4. Add UI controls in `src/ui/components/settings_dialog.py`

---

## 📝 Answer Structure

Every AI response follows this structure:

**Conceptual / Data Engineering questions:**
- ⚡ Short Answer (20-30s verbal)
- 📖 Detailed Explanation
- 💻 Code / Query Example
- 🌍 Real-World Example
- ✅ Best Practices
- ❌ Common Mistakes
- ⚙️ Performance Considerations
- 🔄 Alternatives
- ❓ Follow-up Questions

**Coding / DSA questions:**
- 🎯 Problem Summary
- 🤔 Clarifying Questions
- 💡 Brute Force → Better → Optimal approach
- ✅ Production-Ready Code
- 📊 Time & Space Complexity
- 🧪 Dry Run
- ⚠️ Edge Cases
- 🧪 Test Cases
- 💬 Interview Explanation

---

## 📋 Requirements

- Python 3.10+
- Windows 10/11 (primary), macOS, Linux
- At least one API key (OpenAI / Claude / Gemini) **or** Ollama running locally
- Microphone (for speech recognition)
- Tesseract OCR (optional, for screenshot questions)

---

## 🛠 Troubleshooting

**App doesn't start:**
```bash
pip install --upgrade PySide6
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
```

**Speech recognition not working:**
```bash
pip install sounddevice faster-whisper
python -c "import sounddevice; print(sounddevice.query_devices())"
```

**No AI response:**
- Check `.env` has a valid API key
- Check internet connection
- Try switching to `AI_PROVIDER=ollama` for offline mode

**OCR not working:**
- Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Set `TESSERACT_PATH` in `.env`

---

## 📄 License

MIT License — free for personal and commercial use.
