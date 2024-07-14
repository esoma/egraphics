__all__ = [
    "GlBuffer",
    "GlBufferTarget",
    "GlBufferUsage",
    "GlVertexArray",
    "GlType",
    "GL_ARRAY_BUFFER",
    "GL_COPY_READ_BUFFER",
    "GL_ELEMENT_ARRAY_BUFFER",
    "GL_STREAM_DRAW",
    "GL_STREAM_READ",
    "GL_STREAM_COPY",
    "GL_STATIC_DRAW",
    "GL_STATIC_READ",
    "GL_STATIC_COPY",
    "GL_DYNAMIC_DRAW",
    "GL_DYNAMIC_READ",
    "GL_DYNAMIC_COPY",
    "activate_gl_vertex_array",
    "set_gl_buffer_target",
    "create_gl_buffer",
    "create_gl_vertex_array",
    "delete_gl_buffer",
    "delete_gl_vertex_array",
    "set_gl_buffer_target_data",
    "create_gl_copy_read_buffer_memory_view",
    "release_gl_copy_read_buffer_memory_view",
    "configure_gl_vertex_array_location",
    "set_read_framebuffer",
    "read_color_from_framebuffer",
    "read_depth_from_framebuffer",
]

# egeometry
from egeometry import IRectangle

# emath
from emath import FArray
from emath import FVector4Array

# python
from collections.abc import Buffer
from typing import NewType

GlBuffer = NewType("GlBuffer", int)
GlBufferTarget = NewType("GlBufferTarget", int)
GlBufferUsage = NewType("GlBufferUsage", int)
GlVertexArray = NewType("GlVertexArray", int)
GlType = NewType("GlType", int)

GL_ARRAY_BUFFER: GlBufferTarget
GL_COPY_READ_BUFFER: GlBufferTarget
GL_ELEMENT_ARRAY_BUFFER: GlBufferTarget

GL_STREAM_DRAW: GlBufferUsage
GL_STREAM_READ: GlBufferUsage
GL_STREAM_COPY: GlBufferUsage
GL_STATIC_DRAW: GlBufferUsage
GL_STATIC_READ: GlBufferUsage
GL_STATIC_COPY: GlBufferUsage
GL_DYNAMIC_DRAW: GlBufferUsage
GL_DYNAMIC_READ: GlBufferUsage
GL_DYNAMIC_COPY: GlBufferUsage

GL_FLOAT: GlType
GL_DOUBLE: GlType
GL_BYTE: GlType
GL_UNSIGNED_BYTE: GlType
GL_SHORT: GlType
GL_UNSIGNED_SHORT: GlType
GL_INT: GlType
GL_UNSIGNED_INT: GlType

def activate_gl_vertex_array(gl_vertex_array: GlVertexArray | None) -> None: ...
def set_gl_buffer_target(target: GlBufferTarget, gl_buffer: GlBuffer | None, /) -> None: ...
def create_gl_buffer() -> GlBuffer: ...
def create_gl_vertex_array() -> GlVertexArray: ...
def delete_gl_buffer(gl_buffer: GlBuffer, /) -> None: ...
def delete_gl_vertex_array(gl_vertex_array: GlVertexArray, /) -> None: ...
def set_gl_buffer_target_data(
    target: GlBufferTarget, data: Buffer | int, usage: GlBufferUsage, /
) -> int: ...
def create_gl_copy_read_buffer_memory_view(length: int) -> memoryview: ...
def release_gl_copy_read_buffer_memory_view() -> None: ...
def configure_gl_vertex_array_location(
    location: int,
    size: int,
    type: GlType,
    stride: int,
    offset: int,
    instancing_divistor: int | None,
    /,
) -> None: ...
def set_read_framebuffer() -> None: ...
def read_color_from_framebuffer(rect: IRectangle, /) -> FVector4Array: ...
def read_depth_from_framebuffer(rect: IRectangle, /) -> FArray: ...
