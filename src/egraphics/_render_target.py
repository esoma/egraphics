from __future__ import annotations

__all__ = [
    "read_color_from_render_target",
    "read_depth_from_render_target",
    "set_read_render_target",
    "clear_render_target",
]


# egraphics
from ._egraphics import clear_framebuffer
from ._egraphics import read_color_from_framebuffer
from ._egraphics import read_depth_from_framebuffer
from ._egraphics import set_read_framebuffer

# egeometry
from egeometry import IRectangle

# emath
from emath import FArray
from emath import FVector3
from emath import FVector4Array

# eplatform
from eplatform import Platform
from eplatform import RenderTarget
from eplatform import set_draw_render_target

_read_render_target: RenderTarget | None = None


@Platform.register_deactivate_callback
def _reset_state_render_target_state() -> None:
    global _read_render_target
    _read_render_target = None


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
