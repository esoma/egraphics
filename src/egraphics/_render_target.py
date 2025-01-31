from __future__ import annotations

__all__ = [
    "read_color_from_render_target",
    "read_depth_from_render_target",
    "set_draw_render_target",
    "set_read_render_target",
    "clear_render_target",
    "RenderTarget",
    "TextureRenderTarget",
    "WindowRenderTargetMixin",
]


# egraphics
from ._egraphics import GlFramebuffer
from ._egraphics import GlRenderbuffer
from ._egraphics import attach_depth_renderbuffer_to_gl_read_framebuffer
from ._egraphics import attach_texture_to_gl_read_framebuffer
from ._egraphics import clear_framebuffer
from ._egraphics import create_gl_framebuffer
from ._egraphics import delete_gl_framebuffer
from ._egraphics import delete_gl_renderbuffer
from ._egraphics import read_color_from_framebuffer
from ._egraphics import read_depth_from_framebuffer
from ._egraphics import set_draw_framebuffer
from ._egraphics import set_read_framebuffer
from ._state import register_reset_state_callback
from ._texture import Texture
from ._texture import get_gl_texture

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
    def _gl_framebuffer(self) -> GlFramebuffer:
        ...

    @property
    def size(self) -> IVector2:
        ...


class TextureRenderTarget:
    __gl_framebuffer: GlFramebuffer | None = None
    _gl_renderbuffers: set[GlRenderbuffer]
    _size: IVector2

    def __init__(self, colors: Texture, *, depth: bool = False):
        self._gl_renderbuffers = set()
        self._size = IVector2(*colors.size)
        self.__gl_framebuffer = create_gl_framebuffer()
        set_read_render_target(self)
        self._colors = colors
        attach_texture_to_gl_read_framebuffer(get_gl_texture(colors))
        if depth:
            self._gl_renderbuffers.add(
                attach_depth_renderbuffer_to_gl_read_framebuffer(self._size)
            )

    def __del__(self) -> None:
        if self.__gl_framebuffer is not None:
            delete_gl_framebuffer(self.__gl_framebuffer)
            self.__gl_framebuffer = None
        for gl_renderbuffer in list(self._gl_renderbuffers):
            delete_gl_renderbuffer(gl_renderbuffer)
            self._gl_renderbuffers.remove(gl_renderbuffer)

    @property
    def _gl_framebuffer(self) -> GlFramebuffer:
        assert self.__gl_framebuffer is not None
        return self.__gl_framebuffer

    @property
    def size(self) -> IVector2:
        return self._size


class WindowRenderTargetMixin:
    def refresh(self, *args: Any, **kwargs: Any) -> Any:
        if sys.platform == "darwin":
            # on macos the window must be bound to the draw framebuffer before swapping
            set_draw_render_target(self)  # type: ignore
        return super().refresh(*args, **kwargs)  # type: ignore

    @property
    def _gl_framebuffer(self) -> GlFramebuffer:
        return GlFramebuffer(0)


_draw_render_target: RenderTarget | None = None
_draw_render_target_size: IVector2 | None = None
_read_render_target: RenderTarget | None = None


@register_reset_state_callback
def _reset_state_render_target_state() -> None:
    global _draw_render_target
    global _draw_render_target_size
    global _read_render_target
    _draw_render_target = None
    _draw_render_target_size = None
    _read_render_target = None


def set_draw_render_target(render_target: RenderTarget) -> None:
    global _draw_render_target
    global _draw_render_target_size
    if _draw_render_target is render_target and render_target.size == _draw_render_target_size:
        return
    set_draw_framebuffer(render_target._gl_framebuffer, render_target.size)
    _draw_render_target = render_target
    _draw_render_target_size = render_target.size


def set_read_render_target(render_target: RenderTarget) -> None:
    global _read_render_target
    if _read_render_target is render_target:
        return
    set_read_framebuffer(render_target._gl_framebuffer)
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
