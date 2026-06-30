"""Global hotkey registration using the keyboard library."""

from __future__ import annotations

import threading
from typing import Callable, Dict

from ..utils.logger import get_logger

log = get_logger("hotkeys")

_DEFAULT_BINDINGS: Dict[str, str] = {
    "start_listening":  "ctrl+shift+s",
    "stop_listening":   "ctrl+shift+x",
    "toggle_window":    "ctrl+shift+h",
    "copy_answer":      "ctrl+shift+c",
    "ocr_capture":      "ctrl+shift+o",
    "pin_window":       "ctrl+shift+p",
    "clear_screen":     "ctrl+shift+l",
}


class HotkeyManager:
    def __init__(self, bindings: Dict[str, str] | None = None):
        self._bindings = bindings or _DEFAULT_BINDINGS
        self._handlers: Dict[str, Callable] = {}
        self._registered: list[str] = []

    def register(self, action: str, handler: Callable) -> None:
        self._handlers[action] = handler

    def start(self) -> None:
        try:
            import keyboard
            for action, hotkey in self._bindings.items():
                handler = self._handlers.get(action)
                if handler:
                    try:
                        keyboard.add_hotkey(hotkey, handler, suppress=False)
                        self._registered.append(hotkey)
                        log.debug("Registered hotkey %s → %s", hotkey, action)
                    except Exception as e:
                        log.warning("Could not register hotkey %s: %s", hotkey, e)
            log.info("Hotkeys active: %s", self._registered)
        except ImportError:
            log.warning("keyboard library not installed — hotkeys disabled")

    def stop(self) -> None:
        try:
            import keyboard
            keyboard.unhook_all()
        except Exception:
            pass
