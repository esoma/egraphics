from __future__ import annotations

__all__ = [
    "read_color_from_render_target",
    "read_depth_from_render_target",
    "set_draw_render_target",
    "set_read_render_target",
    "clear_render_target",
    "RenderTarget",
    "WindowRenderTargetMixin",
]


# egraphics
from ._egraphics import clear_framebuffer
from ._egraphics import read_color_from_framebuffer
from ._egraphics import read_depth_from_framebuffer
from ._egraphics import set_draw_framebuffer
from ._egraphics import set_read_framebuffer
from ._state import register_reset_state_callback

# egeometry
from egeometry import IRectangle

# emath
from emath import FArray
from emath import FVector3
from emath import FVector4Array
from emath import IVector2

# python
import sys
from typing import Any
from typing import Protocol


class RenderTarget(Protocol):
    @property
    def _gl_framebuffer(self) -> int:
        ...

    @property
    def size(self) -> IVector2:
        ...


class WindowRenderTargetMixin:
    size: IVector2

    def refresh(self, *args: Any, **kwargs: Any) -> Any:
        if sys.platform == "darwin":
            # on macos the window must be bound to the draw framebuffer before swapping
            set_draw_render_target(self)
        return super().refresh(*args, **kwargs)  # type: ignore

    @property
    def _gl_framebuffer(self) -> int:
        return 0


_draw_render_target: RenderTarget | None = None
_read_render_target: RenderTarget | None = None


@register_reset_state_callback
def _reset_state_render_target_state() -> None:
    global _draw_render_target
    global _read_render_target
    _draw_render_target = None
    _read_render_target = None


def set_draw_render_target(render_target: RenderTarget) -> None:
    global _draw_render_target
    if _draw_render_target is render_target:
        return
    set_draw_framebuffer(render_target._gl_framebuffer, render_target.size)
    _draw_render_target = render_target


def set_read_render_target(render_target: RenderTarget) -> None:
    global _read_render_target
    if _read_render_target is render_target:
        return
    set_read_framebuffer()
    _read_render_target = render_target


def read_color_from_render_target(render_target: RenderTarget, rect: IRectangle) -> FVector4Array:
    set_read_render_target(render_target)
    return read_color_from_framebuffer(rect)


def read_depth_from_render_target(render_target: RenderTarget, rect: IRectangle) -> FArray:
    set_read_render_target(render_target)
    return read_depth_from_framebuffer(rect)


def clear_render_target(
    render_target: RenderTarget, *, color: FVector3 | None = None, depth: float | None = None
) -> None:
    set_draw_render_target(render_target)
    clear_framebuffer(color, depth)
