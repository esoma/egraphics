from __future__ import annotations

__all__ = ["clear_cache"]


from ._egraphics import GL_BUFFER_UPDATE_BARRIER_BIT
from ._egraphics import GL_ELEMENT_ARRAY_BARRIER_BIT
from ._egraphics import GL_SHADER_IMAGE_ACCESS_BARRIER_BIT
from ._egraphics import GL_SHADER_STORAGE_BARRIER_BIT
from ._egraphics import GL_TEXTURE_UPDATE_BARRIER_BIT
from ._egraphics import GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT
from ._egraphics import set_gl_memory_barrier


def clear_cache(
    *,
    shader_image: bool = False,
    shader_texture: bool = False,
    shader_storage_buffer: bool = False,
    shader_indices: bool = False,
    shader_attributes: bool = False,
    g_buffer: bool = False,
) -> None:
    barriers = 0
    if shader_image:
        barriers |= GL_SHADER_IMAGE_ACCESS_BARRIER_BIT
    if shader_texture:
        barriers |= GL_TEXTURE_UPDATE_BARRIER_BIT
    if shader_storage_buffer:
        barriers |= GL_SHADER_STORAGE_BARRIER_BIT
    if shader_indices:
        barriers |= GL_ELEMENT_ARRAY_BARRIER_BIT
    if shader_attributes:
        barriers |= GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT
    if g_buffer:
        barriers |= GL_BUFFER_UPDATE_BARRIER_BIT
    if barriers != 0:
        set_gl_memory_barrier(barriers)  # type: ignore
