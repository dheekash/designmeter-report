#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║         Interview Helper — One-File Installer        ║
║         Run:  py INSTALL.py  (no deps needed)        ║
╚══════════════════════════════════════════════════════╝

This single script handles everything:
  • System checks (Python version, disk space)
  • Virtual environment creation
  • Dependency installation
  • Interactive .env configuration (with GUI dialog)
  • Whisper model pre-download (optional)
  • Desktop shortcut creation (Windows)
  • Test run to verify installation
  • App launch

Usage:
    py INSTALL.py              → full interactive install
    py INSTALL.py --silent     → non-interactive (uses defaults)
    py INSTALL.py --repair     → reinstall deps only
    py INSTALL.py --launch     → skip install, just run the app
"""

# ── stdlib only (no pip needed to run this script) ──────────────────────────
import os
import sys
import subprocess
import shutil
import platform
import argparse
import time
import textwrap
import json
import re
from pathlib import Path
from urllib.request import urlretrieve
from typing import Optional

# ── Globals ──────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.resolve()
VENV_DIR    = ROOT / ".venv"
ENV_FILE    = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
REQ_FILE    = ROOT / "requirements.txt"
MAIN_PY     = ROOT / "main.py"

MIN_PYTHON  = (3, 10)
MAX_PYTHON  = (3, 13)   # PySide6 has no wheel for 3.14+ yet
MIN_DISK_MB = 2000   # 2 GB for models + deps

IS_WINDOWS = platform.system() == "Windows"
IS_MAC     = platform.system() == "Darwin"


# ── Terminal colours (no external lib needed) ────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    BG_BLUE = "\033[44m"

    @staticmethod
    def enable():
        if IS_WINDOWS:
            os.system("color")          # enable ANSI on Windows


C.enable()


def _w(text: str, *codes: str) -> str:
    return "".join(codes) + text + C.RESET


def banner():
    print()
    print(_w("╔══════════════════════════════════════════════════════════╗", C.BLUE, C.BOLD))
    print(_w("║                                                          ║", C.BLUE, C.BOLD))
    print(_w("║   ✦  ", C.BLUE, C.BOLD) + _w("Interview Helper", C.CYAN, C.BOLD) + _w(" — Installer v1.0          ║", C.BLUE, C.BOLD))
    print(_w("║      Real-time AI Interview Assistant                    ║", C.BLUE, C.BOLD))
    print(_w("║                                                          ║", C.BLUE, C.BOLD))
    print(_w("╚══════════════════════════════════════════════════════════╝", C.BLUE, C.BOLD))
    print()


def step(n: int, total: int, title: str):
    bar = f"[{n}/{total}]"
    print(f"\n{_w(bar, C.YELLOW, C.BOLD)} {_w(title, C.WHITE, C.BOLD)}")
    print(_w("─" * 58, C.DIM))


def ok(msg: str):
    print(f"  {_w('✔', C.GREEN, C.BOLD)}  {msg}")


def warn(msg: str):
    print(f"  {_w('⚠', C.YELLOW, C.BOLD)}  {msg}")


def err(msg: str):
    print(f"  {_w('✘', C.RED, C.BOLD)}  {msg}")


def info(msg: str):
    print(f"  {_w('·', C.CYAN)}  {msg}")


def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    try:
        val = input(f"  {_w('?', C.CYAN, C.BOLD)}  {prompt}{hint}: ").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        return default


def ask_secret(prompt: str) -> str:
    import getpass
    try:
        return getpass.getpass(f"  {_w('🔑', C.CYAN)}  {prompt}: ").strip()
    except Exception:
        return ask(prompt)


def confirm(prompt: str, default: bool = True) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    try:
        val = input(f"  {_w('?', C.CYAN, C.BOLD)}  {prompt} {hint}: ").strip().lower()
        if not val:
            return default
        return val in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return default


def run_cmd(cmd: list, cwd: Path = ROOT, capture: bool = False, env: dict = None) -> subprocess.CompletedProcess:
    merged_env = {**os.environ, **(env or {})}
    if capture:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=merged_env)
    return subprocess.run(cmd, cwd=cwd, env=merged_env)


def spinner(msg: str, duration: float = 0.5):
    """Simple inline spinner for short waits."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r  {_w(frames[i % len(frames)], C.CYAN)}  {msg}", end="", flush=True)
        time.sleep(0.08)
        i += 1
    print(f"\r  {_w('✔', C.GREEN, C.BOLD)}  {msg}  ", flush=True)


# ── Step 1: System checks ────────────────────────────────────────────────────

def check_system() -> bool:
    step(1, 7, "System Requirements")

    # Python version
    v = sys.version_info
    if (v.major, v.minor) < MIN_PYTHON:
        err(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required — found {v.major}.{v.minor}")
        err("Download from https://python.org")
        return False
    if (v.major, v.minor) > MAX_PYTHON:
        warn(f"Python {v.major}.{v.minor} detected — PySide6 requires Python ≤ 3.13")
        warn("Download Python 3.13 from https://python.org/downloads/release/python-3130/")
        warn("Then run:  py -3.13 INSTALL.py")
        if not confirm("Continue anyway? (may fail at PySide6 install)", default=False):
            return False
    else:
        ok(f"Python {v.major}.{v.minor}.{v.micro} ✓")

    # Disk space
    try:
        stat = shutil.disk_usage(ROOT)
        free_mb = stat.free // (1024 * 1024)
        if free_mb < MIN_DISK_MB:
            warn(f"Low disk space: {free_mb} MB free (recommend {MIN_DISK_MB} MB+)")
        else:
            ok(f"Disk space: {free_mb:,} MB free ✓")
    except Exception:
        warn("Could not check disk space")

    # Internet
    try:
        import urllib.request
        urllib.request.urlopen("https://pypi.org", timeout=4)
        ok("Internet connection ✓")
    except Exception:
        warn("No internet — will use cached packages if available")

    # pip
    result = run_cmd([sys.executable, "-m", "pip", "--version"], capture=True)
    if result.returncode == 0:
        ok("pip ✓")
    else:
        err("pip not found — trying to bootstrap")
        run_cmd([sys.executable, "-m", "ensurepip", "--upgrade"])

    # Tesseract (optional)
    tesseract_found = shutil.which("tesseract") is not None
    if tesseract_found:
        ok("Tesseract OCR ✓")
    else:
        warn("Tesseract OCR not found (optional — needed for screenshot questions)")
        info("Install from: https://github.com/UB-Mannheim/tesseract/wiki")

    # ffmpeg (optional, helps whisper)
    if shutil.which("ffmpeg"):
        ok("ffmpeg ✓")
    else:
        warn("ffmpeg not found (optional — some audio formats may not work)")

    return True


# ── Step 2: Virtual environment ───────────────────────────────────────────────

def setup_venv(repair: bool = False) -> Path:
    step(2, 7, "Virtual Environment")

    if VENV_DIR.exists() and not repair:
        ok(f"Virtual environment already exists at {VENV_DIR.name}/")
        return _venv_python()

    if VENV_DIR.exists() and repair:
        info("Removing existing venv for repair…")
        shutil.rmtree(VENV_DIR)

    info("Creating virtual environment…")
    result = run_cmd([sys.executable, "-m", "venv", str(VENV_DIR)])
    if result.returncode != 0:
        err("Failed to create virtual environment")
        sys.exit(1)

    ok(f"Created: {VENV_DIR}")
    return _venv_python()


def _venv_python() -> Path:
    if IS_WINDOWS:
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _venv_pip() -> Path:
    if IS_WINDOWS:
        return VENV_DIR / "Scripts" / "pip.exe"
    return VENV_DIR / "bin" / "pip"


# ── Step 3: Install dependencies ─────────────────────────────────────────────

# Core packages (always install)
_CORE_PACKAGES = [
    "PySide6>=6.6.0",
    "openai>=1.35.0",
    "anthropic>=0.28.0",
    "google-generativeai>=0.5.0",
    "faster-whisper>=1.0.0",
    "sounddevice>=0.4.6",
    "numpy>=1.24.0",
    "scipy>=1.11.0",
    "sqlalchemy>=2.0.0",
    "pygments>=2.17.0",
    "pillow>=10.0.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    "pyperclip>=1.8.2",
    "mss>=9.0.1",
    "keyboard>=0.13.5",
    "markdown>=3.5.0",
    "reportlab>=4.0.0",
    "jinja2>=3.1.0",
]

# Optional (ask user)
_OPTIONAL_PACKAGES = {
    "pytesseract": "OCR for screenshot questions (requires Tesseract binary)",
    "easyocr":     "Alternative OCR engine (heavy — ~1 GB download)",
    "reportlab":   "PDF export support",
}


def install_deps(venv_py: Path, silent: bool = False):
    step(3, 7, "Installing Dependencies")

    pip = [str(venv_py), "-m", "pip"]

    # Upgrade pip silently
    info("Upgrading pip…")
    run_cmd([*pip, "install", "--upgrade", "pip", "--quiet"], capture=True)

    # Install from requirements.txt if it exists
    if REQ_FILE.exists():
        info(f"Installing from {REQ_FILE.name}…")
        print()
        result = run_cmd([*pip, "install", "-r", str(REQ_FILE)])
        if result.returncode != 0:
            warn("Some packages failed — retrying core packages individually…")
            _install_individually(pip)
    else:
        _install_individually(pip)

    ok("All core packages installed")

    # Optional packages
    if not silent:
        print()
        info("Optional packages (press Enter to skip):")
        for pkg, desc in _OPTIONAL_PACKAGES.items():
            if confirm(f"  Install {_w(pkg, C.CYAN)}? ({desc})", default=False):
                run_cmd([*pip, "install", pkg, "--quiet"])
                ok(f"{pkg} installed")


def _install_individually(pip: list):
    for pkg in _CORE_PACKAGES:
        name = pkg.split(">=")[0].split("==")[0]
        info(f"Installing {name}…")
        result = run_cmd([*pip, "install", pkg, "--quiet"], capture=True)
        if result.returncode == 0:
            ok(f"{name} ✓")
        else:
            warn(f"{name} failed — {result.stderr.strip()[:80]}")


# ── Step 4: Configure .env ────────────────────────────────────────────────────

def configure_env(silent: bool = False):
    step(4, 7, "AI Configuration")

    if ENV_FILE.exists() and not silent:
        if not confirm("A .env file already exists. Reconfigure?", default=False):
            ok("Keeping existing .env")
            _show_current_config()
            return

    # Load example as base
    env_content = ENV_EXAMPLE.read_text(encoding="utf-8") if ENV_EXAMPLE.exists() else ""
    config: dict = _parse_env(env_content)

    if silent:
        # Just copy .env.example if no .env
        if not ENV_FILE.exists():
            ENV_FILE.write_text(env_content, encoding="utf-8")
            warn("Created .env from template — add API keys before running!")
        return

    # ── Provider selection ───────────────────────────────────────────
    print()
    print(f"  {_w('Choose your AI provider:', C.WHITE, C.BOLD)}")
    print(f"  {_w('1', C.CYAN, C.BOLD)}  OpenAI       (GPT-4o — best for coding)")
    print(f"  {_w('2', C.CYAN, C.BOLD)}  Claude       (Anthropic — best explanations)")
    print(f"  {_w('3', C.CYAN, C.BOLD)}  Gemini       (Google — good for data)")
    print(f"  {_w('4', C.CYAN, C.BOLD)}  Ollama       (Offline — no API key needed)")
    print(f"  {_w('5', C.CYAN, C.BOLD)}  Configure all providers")
    print()

    choice = ask("Your choice", default="1")

    providers_to_configure = {
        "1": ["openai"],
        "2": ["claude"],
        "3": ["gemini"],
        "4": ["ollama"],
        "5": ["openai", "claude", "gemini", "ollama"],
    }.get(choice, ["openai"])

    primary_provider = {
        "1": "openai", "2": "claude", "3": "gemini", "4": "ollama", "5": "openai"
    }.get(choice, "openai")

    config["AI_PROVIDER"] = primary_provider

    for provider in providers_to_configure:
        _configure_provider(provider, config)

    # ── Whisper model ────────────────────────────────────────────────
    print()
    print(f"  {_w('Whisper Model (Speech Recognition):', C.WHITE, C.BOLD)}")
    print(f"  {_w('1', C.CYAN)}  tiny    — Fastest,  ~39 MB  (good for fast machines)")
    print(f"  {_w('2', C.CYAN)}  base    — Balanced, ~74 MB  {_w('[RECOMMENDED]', C.GREEN, C.BOLD)}")
    print(f"  {_w('3', C.CYAN)}  small   — Better,  ~244 MB")
    print(f"  {_w('4', C.CYAN)}  medium  — High,    ~769 MB")
    print(f"  {_w('5', C.CYAN)}  large-v3 — Best,  ~1550 MB (needs 8+ GB RAM)")
    print()

    model_choice = ask("Whisper model", default="2")
    model_map = {"1": "tiny", "2": "base", "3": "small", "4": "medium", "5": "large-v3"}
    config["WHISPER_MODEL"] = model_map.get(model_choice, "base")

    # Device (CUDA check)
    cuda_available = _check_cuda()
    if cuda_available:
        use_cuda = confirm("CUDA GPU detected — use it for faster transcription?", default=True)
        config["WHISPER_DEVICE"] = "cuda" if use_cuda else "cpu"
    else:
        config["WHISPER_DEVICE"] = "cpu"

    # ── UI Theme ─────────────────────────────────────────────────────
    print()
    theme = ask("Default theme (dark/light)", default="dark")
    config["DEFAULT_THEME"] = theme if theme in ("dark", "light") else "dark"

    # ── Resume path ──────────────────────────────────────────────────
    print()
    resume = ask("Path to your resume file (PDF/TXT, optional — for personalized answers)", default="")
    if resume and Path(resume).exists():
        config["RESUME_PATH"] = resume
        ok("Resume loaded — answers will be personalised to your experience")

    # Write .env
    _write_env(config)
    ok(f".env saved → {ENV_FILE}")


def _configure_provider(provider: str, config: dict):
    print()
    if provider == "openai":
        print(f"  {_w('OpenAI Setup', C.WHITE, C.BOLD)}")
        info("Get your key at: https://platform.openai.com/api-keys")
        key = ask_secret("OpenAI API Key (sk-...)")
        if key:
            config["OPENAI_API_KEY"] = key
            model = ask("Model", default="gpt-4o")
            config["OPENAI_MODEL"] = model

    elif provider == "claude":
        print(f"  {_w('Anthropic Claude Setup', C.WHITE, C.BOLD)}")
        info("Get your key at: https://console.anthropic.com/")
        key = ask_secret("Anthropic API Key (sk-ant-...)")
        if key:
            config["ANTHROPIC_API_KEY"] = key
            model = ask("Model", default="claude-sonnet-4-6")
            config["CLAUDE_MODEL"] = model

    elif provider == "gemini":
        print(f"  {_w('Google Gemini Setup', C.WHITE, C.BOLD)}")
        info("Get your key at: https://aistudio.google.com/app/apikey")
        key = ask_secret("Gemini API Key (AIza...)")
        if key:
            config["GEMINI_API_KEY"] = key
            model = ask("Model", default="gemini-1.5-pro")
            config["GEMINI_MODEL"] = model

    elif provider == "ollama":
        print(f"  {_w('Ollama (Offline) Setup', C.WHITE, C.BOLD)}")
        info("Make sure Ollama is running: https://ollama.com/download")
        url = ask("Ollama URL", default="http://localhost:11434")
        model = ask("Model", default="llama3.1")
        config["OLLAMA_BASE_URL"] = url
        config["OLLAMA_MODEL"] = model
        info("Pull the model with:  ollama pull llama3.1")


def _check_cuda() -> bool:
    try:
        result = run_cmd(["nvidia-smi"], capture=True)
        return result.returncode == 0
    except Exception:
        return False


def _parse_env(content: str) -> dict:
    config = {}
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            config[k.strip()] = v.strip()
    return config


def _write_env(config: dict):
    # Load example as template to preserve comments
    template = ENV_EXAMPLE.read_text(encoding="utf-8") if ENV_EXAMPLE.exists() else ""
    lines = []
    for line in template.splitlines():
        if line.strip().startswith("#") or not line.strip():
            lines.append(line)
            continue
        if "=" in line:
            k = line.split("=")[0].strip()
            if k in config:
                v = config[k]
                lines.append(f"{k}={v}")
                continue
        lines.append(line)

    # Append any keys not in template
    existing_keys = {l.split("=")[0].strip() for l in template.splitlines() if "=" in l and not l.strip().startswith("#")}
    for k, v in config.items():
        if k not in existing_keys:
            lines.append(f"{k}={v}")

    ENV_FILE.write_text("\n".join(lines), encoding="utf-8")


def _show_current_config():
    if not ENV_FILE.exists():
        return
    cfg = _parse_env(ENV_FILE.read_text(encoding="utf-8"))
    provider = cfg.get("AI_PROVIDER", "?")
    model = cfg.get("OPENAI_MODEL") or cfg.get("CLAUDE_MODEL") or cfg.get("GEMINI_MODEL") or cfg.get("OLLAMA_MODEL", "?")
    whisper = cfg.get("WHISPER_MODEL", "?")
    info(f"Provider: {provider}  |  Model: {model}  |  Whisper: {whisper}")


# ── Step 5: Pre-download Whisper model ───────────────────────────────────────

def predownload_whisper(venv_py: Path, silent: bool = False):
    step(5, 7, "Whisper Model")

    cfg = _parse_env(ENV_FILE.read_text(encoding="utf-8")) if ENV_FILE.exists() else {}
    model_size = cfg.get("WHISPER_MODEL", "base")
    device = cfg.get("WHISPER_DEVICE", "cpu")

    if not silent:
        if not confirm(f"Pre-download Whisper '{model_size}' model now? (saves time at first use)", default=True):
            warn("Whisper model will download on first use")
            return

    info(f"Downloading faster-whisper '{model_size}' model…")
    script = textwrap.dedent(f"""
        try:
            from faster_whisper import WhisperModel
            print("Downloading model: {model_size}")
            m = WhisperModel("{model_size}", device="{device}", compute_type="int8")
            print("OK")
        except ImportError:
            print("SKIP: faster_whisper not installed")
        except Exception as e:
            print(f"ERROR: {{e}}")
    """)

    result = run_cmd([str(venv_py), "-c", script], capture=True)
    output = (result.stdout + result.stderr).strip()

    if "OK" in output:
        ok(f"Whisper '{model_size}' ready")
    elif "SKIP" in output:
        warn("faster-whisper not installed — speech recognition won't work")
    else:
        warn(f"Download failed or partial: {output[:100]}")
        info("It will retry automatically on first launch")


# ── Step 6: Verify installation ───────────────────────────────────────────────

def verify_install(venv_py: Path):
    step(6, 7, "Verification")

    checks = {
        "PySide6":        "from PySide6.QtWidgets import QApplication; print('OK')",
        "faster-whisper": "from faster_whisper import WhisperModel; print('OK')",
        "sounddevice":    "import sounddevice; print('OK')",
        "sqlalchemy":     "import sqlalchemy; print('OK')",
        "pygments":       "import pygments; print('OK')",
        "openai":         "import openai; print('OK')",
        "anthropic":      "import anthropic; print('OK')",
    }

    all_ok = True
    for name, code in checks.items():
        result = run_cmd([str(venv_py), "-c", code], capture=True)
        if "OK" in result.stdout:
            ok(f"{name}")
        else:
            warn(f"{name} — {result.stderr.strip()[:60] or 'not found'}")
            all_ok = False

    # Verify our own imports
    verify_script = textwrap.dedent("""
        import sys
        sys.path.insert(0, '.')
        from src.ai.detector import detect_category
        assert detect_category("What is a SQL JOIN?") == "SQL"
        from src.utils.cache import ResponseCache
        c = ResponseCache(); c.set("q","SQL","openai",{"a":"test"})
        assert c.get("q","SQL","openai") is not None
        print("CORE_OK")
    """)
    result = run_cmd([str(venv_py), "-c", verify_script], cwd=ROOT, capture=True)
    if "CORE_OK" in result.stdout:
        ok("Core logic verified ✓")
    else:
        warn(f"Core verify failed: {result.stderr.strip()[:80]}")
        all_ok = False

    return all_ok


# ── Step 7: Shortcuts & launch ────────────────────────────────────────────────

def create_shortcuts(venv_py: Path, silent: bool = False):
    step(7, 7, "Finishing Up")

    if IS_WINDOWS and not silent:
        if confirm("Create desktop shortcut?", default=True):
            _create_windows_shortcut(venv_py)

    # Create a convenient launcher script
    if IS_WINDOWS:
        launcher = ROOT / "Launch Interview Helper.bat"
        launcher.write_text(
            f'@echo off\nstart "" "{venv_py}" "{MAIN_PY}"\n',
            encoding="utf-8"
        )
        ok(f"Launcher created: {launcher.name}")

    print()
    print(_w("─" * 58, C.DIM))
    print()
    print(_w("  ✦  Installation Complete!", C.GREEN, C.BOLD))
    print()
    print(f"  {_w('To run:', C.WHITE, C.BOLD)}")
    if IS_WINDOWS:
        print(f"    Double-click:  {_w('Launch Interview Helper.bat', C.CYAN)}")
        print(f"    Or command:    {_w('py INSTALL.py --launch', C.CYAN)}")
    else:
        print(f"    Command:       {_w('.venv/bin/python main.py', C.CYAN)}")
    print()

    # Check if API key is configured
    cfg = _parse_env(ENV_FILE.read_text(encoding="utf-8")) if ENV_FILE.exists() else {}
    has_key = any([
        cfg.get("OPENAI_API_KEY", "").startswith("sk-"),
        cfg.get("ANTHROPIC_API_KEY", "").startswith("sk-ant-"),
        cfg.get("GEMINI_API_KEY", "").startswith("AIza"),
        cfg.get("AI_PROVIDER") == "ollama",
    ])

    if not has_key:
        print(f"  {_w('⚠  No API key configured!', C.YELLOW, C.BOLD)}")
        print(f"  Edit {_w('.env', C.CYAN)} and add at least one API key before running.")
        print()

    if not silent:
        if confirm("Launch Interview Helper now?", default=has_key):
            launch_app(venv_py)


def _create_windows_shortcut(venv_py: Path):
    try:
        import winreg
        desktop = Path.home() / "Desktop"
        script = textwrap.dedent(f"""
            Set objWS = WScript.CreateObject("WScript.Shell")
            sLnk = "{desktop / 'Interview Helper.lnk'}"
            Set oLnk = objWS.CreateShortcut(sLnk)
            oLnk.TargetPath = "{venv_py}"
            oLnk.Arguments = "{MAIN_PY}"
            oLnk.WorkingDirectory = "{ROOT}"
            oLnk.Description = "Interview Helper — AI Interview Assistant"
            oLnk.Save
        """)
        vbs = ROOT / "_shortcut.vbs"
        vbs.write_text(script, encoding="utf-8")
        subprocess.run(["cscript", "//nologo", str(vbs)], capture_output=True)
        vbs.unlink(missing_ok=True)
        ok("Desktop shortcut created")
    except Exception as e:
        warn(f"Could not create shortcut: {e}")


def launch_app(venv_py: Path):
    print()
    info("Launching Interview Helper…")
    time.sleep(0.5)
    if IS_WINDOWS:
        subprocess.Popen(
            [str(venv_py), str(MAIN_PY)],
            cwd=ROOT,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        subprocess.Popen([str(venv_py), str(MAIN_PY)], cwd=ROOT)
    ok("App launched!")


# ── GUI mode (tkinter fallback for key entry) ─────────────────────────────────

def _try_gui_config():
    """If running without a proper terminal, open a Tk dialog for API key."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog

        root = tk.Tk()
        root.title("Interview Helper — Quick Setup")
        root.resizable(False, False)

        _style_tk(root)

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="✦ Interview Helper Setup", font=("Segoe UI", 16, "bold")).pack(pady=(0, 16))
        ttk.Label(frame, text="Choose AI Provider:").pack(anchor="w")

        provider_var = tk.StringVar(value="openai")
        providers = [("OpenAI (GPT-4o)", "openai"), ("Claude (Anthropic)", "claude"),
                     ("Gemini (Google)", "gemini"), ("Ollama (Offline)", "ollama")]
        for label, val in providers:
            ttk.Radiobutton(frame, text=label, variable=provider_var, value=val).pack(anchor="w", padx=8)

        ttk.Separator(frame).pack(fill="x", pady=12)
        ttk.Label(frame, text="API Key:").pack(anchor="w")
        key_var = tk.StringVar()
        key_entry = ttk.Entry(frame, textvariable=key_var, show="*", width=48)
        key_entry.pack(fill="x", pady=(4, 0))

        ttk.Separator(frame).pack(fill="x", pady=12)
        ttk.Label(frame, text="Whisper Model:").pack(anchor="w")
        whisper_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(frame, textvariable=whisper_var,
                                   values=["tiny", "base", "small", "medium", "large-v3"],
                                   state="readonly", width=20)
        model_combo.pack(anchor="w", pady=(4, 0))

        ttk.Separator(frame).pack(fill="x", pady=12)
        result = {"ok": False}

        def on_ok():
            provider = provider_var.get()
            key = key_var.get().strip()
            model = whisper_var.get()

            cfg = _parse_env(ENV_EXAMPLE.read_text(encoding="utf-8") if ENV_EXAMPLE.exists() else "")
            cfg["AI_PROVIDER"] = provider
            cfg["WHISPER_MODEL"] = model
            cfg["WHISPER_DEVICE"] = "cpu"
            cfg["DEFAULT_THEME"] = "dark"

            if key:
                if provider == "openai":
                    cfg["OPENAI_API_KEY"] = key
                elif provider == "claude":
                    cfg["ANTHROPIC_API_KEY"] = key
                elif provider == "gemini":
                    cfg["GEMINI_API_KEY"] = key

            _write_env(cfg)
            result["ok"] = True
            root.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Cancel", command=root.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Save & Continue", command=on_ok).pack(side="right")

        root.mainloop()
        return result["ok"]
    except Exception:
        return False


def _style_tk(root):
    try:
        root.configure(bg="#0d1117")
        style = __import__("tkinter.ttk", fromlist=["Style"]).Style(root)
        style.theme_use("clam")
        style.configure(".", background="#0d1117", foreground="#c9d1d9",
                        fieldbackground="#161b22", font=("Segoe UI", 11))
        style.configure("TButton", background="#21262d", foreground="#c9d1d9",
                        relief="flat", padding=6)
        style.configure("TEntry", fieldbackground="#161b22", foreground="#c9d1d9")
        style.configure("TLabel", background="#0d1117", foreground="#c9d1d9")
        style.configure("TFrame", background="#0d1117")
        style.configure("TSeparator", background="#21262d")
        style.configure("TRadiobutton", background="#0d1117", foreground="#c9d1d9")
        style.configure("TCombobox", fieldbackground="#161b22", foreground="#c9d1d9")
    except Exception:
        pass


# ── Argument parsing & main ───────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Interview Helper Installer")
    parser.add_argument("--silent",  action="store_true", help="Non-interactive install")
    parser.add_argument("--repair",  action="store_true", help="Reinstall all dependencies")
    parser.add_argument("--launch",  action="store_true", help="Just launch the app")
    parser.add_argument("--no-whisper", action="store_true", help="Skip Whisper pre-download")
    parser.add_argument("--config",  action="store_true", help="Reconfigure .env only")
    return parser.parse_args()


def main():
    args = parse_args()

    banner()

    # ── Launch only ──────────────────────────────────────────────────
    if args.launch:
        py = _venv_python()
        if not py.exists():
            err("Virtual environment not found — run installer first")
            sys.exit(1)
        launch_app(py)
        return

    # ── Config only ──────────────────────────────────────────────────
    if args.config:
        configure_env(silent=False)
        return

    # ── Detect headless (no terminal) ────────────────────────────────
    headless = not sys.stdout.isatty() and not args.silent
    if headless:
        print("Detected non-interactive environment — opening GUI setup…")
        _try_gui_config()
        args.silent = True

    # ── Full install ─────────────────────────────────────────────────
    try:
        if not check_system():
            sys.exit(1)

        venv_py = setup_venv(repair=args.repair)
        install_deps(venv_py, silent=args.silent)
        configure_env(silent=args.silent)

        if not args.no_whisper:
            predownload_whisper(venv_py, silent=args.silent)
        else:
            step(5, 7, "Whisper Model")
            warn("Skipped (--no-whisper) — will download on first use")

        all_ok = verify_install(venv_py)
        if not all_ok:
            warn("Some checks failed — the app may still work for core features")

        create_shortcuts(venv_py, silent=args.silent)

    except KeyboardInterrupt:
        print(f"\n\n  {_w('Cancelled.', C.YELLOW)}")
        sys.exit(0)
    except Exception as e:
        err(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
