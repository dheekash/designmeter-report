"""Build a standalone Windows executable using PyInstaller."""

import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent


def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=InterviewHelper",
        "--onefile",
        "--windowed",
        "--icon=assets/icons/app.ico",
        "--add-data=assets;assets",
        "--add-data=.env.example;.",
        "--hidden-import=PySide6.QtSvg",
        "--hidden-import=PySide6.QtPrintSupport",
        "--hidden-import=faster_whisper",
        "--hidden-import=sounddevice",
        "--hidden-import=sqlalchemy.dialects.sqlite",
        "--hidden-import=anthropic",
        "--hidden-import=openai",
        "--hidden-import=google.generativeai",
        "--collect-all=pygments",
        "--collect-all=faster_whisper",
        "--noconfirm",
        "main.py",
    ]

    print("Building executable…")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode == 0:
        exe = ROOT / "dist" / "InterviewHelper.exe"
        print(f"\n✅ Build complete: {exe}")
    else:
        print("\n❌ Build failed")
        sys.exit(1)


if __name__ == "__main__":
    build()
