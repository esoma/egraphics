from __future__ import annotations

__all__ = ["clear_cache"]


from ._egraphics import GL_SHADER_IMAGE_ACCESS_BARRIER_BIT
from ._egraphics import GL_TEXTURE_UPDATE_BARRIER_BIT
from ._egraphics import set_gl_memory_barrier


def clear_cache(*, image: bool = False, texture: bool = False) -> None:
    barriers = 0
    if image:
        barriers |= GL_SHADER_IMAGE_ACCESS_BARRIER_BIT
    if texture:
        barriers |= GL_TEXTURE_UPDATE_BARRIER_BIT
    if barriers != 0:
        set_gl_memory_barrier(barriers)  # type: ignore
