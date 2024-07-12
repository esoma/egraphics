from __future__ import annotations

__all__ = ["register_reset_state_callback", "reset_state"]

# python
from typing import Callable

_reset_callbacks: list[Callable[[], None]] = []


def reset_state() -> None:
    for callback in _reset_callbacks:
        callback()


def register_reset_state_callback(callback: Callable[[], None]) -> Callable[[], None]:
    _reset_callbacks.append(callback)
    return callback
