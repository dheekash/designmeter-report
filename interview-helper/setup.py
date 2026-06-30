"""Package setup (optional — use requirements.txt for direct install)."""

from setuptools import setup, find_packages

setup(
    name="interview-helper",
    version="1.0.0",
    description="Real-time AI interview assistant desktop application",
    author="Dheeraj Kashyap",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.6.0",
        "openai>=1.35.0",
        "anthropic>=0.28.0",
        "google-generativeai>=0.5.0",
        "faster-whisper>=1.0.0",
        "sounddevice>=0.4.6",
        "numpy>=1.24.0",
        "sqlalchemy>=2.0.0",
        "pygments>=2.17.0",
        "keyboard>=0.13.5",
        "pillow>=10.0.0",
        "pytesseract>=0.3.10",
        "markdown>=3.5.0",
        "reportlab>=4.0.0",
        "jinja2>=3.1.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "pyperclip>=1.8.2",
        "mss>=9.0.1",
    ],
    entry_points={
        "console_scripts": [
            "interview-helper=main:main",
        ],
    },
)
