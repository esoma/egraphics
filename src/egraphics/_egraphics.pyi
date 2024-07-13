__all__ = ["bind_gl_buffer", "create_gl_buffer", "GL_ARRAY_BUFFER", "GL_COPY_READ_BUFFER"]

# python
from collections.abc import Buffer
from typing import NewType

GlBuffer = NewType("GlBuffer", int)
GlBufferTarget = NewType("GlBufferTarget", int)
GlBufferUsage = NewType("GlBufferUsage", int)

GL_ARRAY_BUFFER: GlBufferTarget
GL_COPY_READ_BUFFER: GlBufferTarget

GL_STREAM_DRAW: GlBufferUsage
GL_STREAM_READ: GlBufferUsage
GL_STREAM_COPY: GlBufferUsage
GL_STATIC_DRAW: GlBufferUsage
GL_STATIC_READ: GlBufferUsage
GL_STATIC_COPY: GlBufferUsage
GL_DYNAMIC_DRAW: GlBufferUsage
GL_DYNAMIC_READ: GlBufferUsage
GL_DYNAMIC_COPY: GlBufferUsage

def bind_gl_buffer(target: GlBufferTarget, gl_buffer: GlBuffer | None, /) -> None: ...
def create_gl_buffer() -> GlBuffer: ...
def delete_gl_buffer(gl_buffer: GlBuffer, /) -> None: ...
def set_gl_buffer_target_data(
    target: GlBufferTarget, data: Buffer | int, usage: GlBufferUsage, /
) -> int: ...
