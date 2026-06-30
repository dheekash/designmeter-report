@echo off
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python main.py
) else (
    python main.py
)
