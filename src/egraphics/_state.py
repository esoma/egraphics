from __future__ import annotations

__all__ = ["get_gl_version", "register_reset_state_callback", "reset_state"]

from typing import Callable

from ._egraphics import get_gl_version as get_gl_version_string

_reset_state_callbacks: list[Callable[[], None]] = []
_gl_version: tuple[int, int] | None = None


def register_reset_state_callback(callback: Callable[[], None]) -> Callable[[], None]:
    _reset_state_callbacks.append(callback)
    return callback


def reset_state() -> None:
    global _gl_version
    for callback in _reset_state_callbacks:
        callback()
    _gl_version = None


def get_gl_version() -> tuple[int, int]:
    global _gl_version
    if _gl_version is None:
        gl_version = get_gl_version_string()
        _gl_version = tuple(  # type: ignore
            int(v) for v in gl_version.split(" ")[0].split(".")[:2]
        )
    assert _gl_version is not None
    return _gl_version
