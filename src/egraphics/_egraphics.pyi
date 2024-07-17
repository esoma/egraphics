__all__ = [
    "GlBuffer",
    "GlBufferTarget",
    "GlBufferUsage",
    "GlFunc",
    "GlShader",
    "GlVertexArray",
    "GlType",
    "GlTexture",
    "GlTextureComponents",
    "GlTextureFilter",
    "GlTextureTarget",
    "GlTextureWrap",
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
    "GL_RED",
    "GL_RG",
    "GL_RGB",
    "GL_RGBA",
    "GL_CLAMP_TO_EDGE",
    "GL_CLAMP_TO_BORDER",
    "GL_REPEAT",
    "GL_MIRRORED_REPEAT",
    "GL_NEAREST",
    "GL_LINEAR",
    "GL_NEAREST_MIPMAP_NEAREST",
    "GL_NEAREST_MIPMAP_LINEAR",
    "GL_LINEAR_MIPMAP_NEAREST",
    "GL_LINEAR_MIPMAP_LINEAR",
    "GL_TEXTURE_2D",
    "GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_VALUE",
    "GL_NEVER",
    "GL_ALWAYS",
    "GL_LESS",
    "GL_LEQUAL",
    "GL_GREATER",
    "GL_GEQUAL",
    "GL_EQUAL",
    "GL_NOTEQUAL",
    "activate_gl_vertex_array",
    "set_gl_buffer_target",
    "create_gl_buffer",
    "create_gl_vertex_array",
    "create_gl_texture",
    "delete_gl_buffer",
    "delete_gl_vertex_array",
    "delete_gl_texture",
    "set_gl_buffer_target_data",
    "create_gl_copy_read_buffer_memory_view",
    "release_gl_copy_read_buffer_memory_view",
    "configure_gl_vertex_array_location",
    "set_read_framebuffer",
    "read_color_from_framebuffer",
    "read_depth_from_framebuffer",
    "clear_framebuffer",
    "set_active_gl_texture_unit",
    "set_gl_texture_target",
    "set_gl_texture_target_2d_data",
    "generate_gl_texture_target_mipmaps",
    "set_gl_texture_target_filters",
    "get_gl_shader_uniforms",
]

# egeometry
from egeometry import IRectangle

# emath
from emath import FArray
from emath import FVector3
from emath import FVector4
from emath import FVector4Array
from emath import UVector2

# python
from collections.abc import Buffer
from typing import NewType

GlBuffer = NewType("GlBuffer", int)
GlBufferTarget = NewType("GlBufferTarget", int)
GlBufferUsage = NewType("GlBufferUsage", int)
GlFunc = NewType("GlFunc", int)
GlShader = NewType("GlShader", int)
GlVertexArray = NewType("GlVertexArray", int)
GlType = NewType("GlType", int)
GlTexture = NewType("GlTexture", int)
GlTextureComponents = NewType("GlTextureComponents", int)
GlTextureFilter = NewType("GlTextureFilter", int)
GlTextureTarget = NewType("GlTextureTarget", int)
GlTextureWrap = NewType("GlTextureWrap", int)

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

GL_RED: GlTextureComponents
GL_RG: GlTextureComponents
GL_RGB: GlTextureComponents
GL_RGBA: GlTextureComponents

GL_CLAMP_TO_EDGE: GlTextureWrap
GL_CLAMP_TO_BORDER: GlTextureWrap
GL_REPEAT: GlTextureWrap
GL_MIRRORED_REPEAT: GlTextureWrap

GL_NEAREST: GlTextureFilter
GL_LINEAR: GlTextureFilter
GL_NEAREST_MIPMAP_NEAREST: GlTextureFilter
GL_NEAREST_MIPMAP_LINEAR: GlTextureFilter
GL_LINEAR_MIPMAP_NEAREST: GlTextureFilter
GL_LINEAR_MIPMAP_LINEAR: GlTextureFilter

GL_TEXTURE_2D: GlTextureTarget

GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_VALUE: int

GL_NEVER: GlFunc
GL_ALWAYS: GlFunc
GL_LESS: GlFunc
GL_LEQUAL: GlFunc
GL_GREATER: GlFunc
GL_GEQUAL: GlFunc
GL_EQUAL: GlFunc
GL_NOTEQUAL: GlFunc

def activate_gl_vertex_array(gl_vertex_array: GlVertexArray | None) -> None: ...
def set_gl_buffer_target(target: GlBufferTarget, gl_buffer: GlBuffer | None, /) -> None: ...
def create_gl_buffer() -> GlBuffer: ...
def create_gl_vertex_array() -> GlVertexArray: ...
def create_gl_texture() -> GlTexture: ...
def delete_gl_buffer(gl_buffer: GlBuffer, /) -> None: ...
def delete_gl_vertex_array(gl_vertex_array: GlVertexArray, /) -> None: ...
def delete_gl_texture(gl_texture: GlTexture, /) -> None: ...
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
def clear_framebuffer(color: FVector3 | None, depth: float | None, /) -> None: ...
def set_active_gl_texture_unit(unit: int, /) -> None: ...
def set_gl_texture_target(target: GlTextureTarget, gl_texture: GlTexture | None, /) -> None: ...
def set_gl_texture_target_2d_data(
    target: GlTextureTarget,
    format: GlTextureComponents,
    size: UVector2,
    type: GlType,
    data: Buffer,
    /,
) -> None: ...
def generate_gl_texture_target_mipmaps(target: GlTextureTarget, /) -> None: ...
def set_gl_texture_target_parameters(
    target: GlTextureTarget,
    min_filter: GlTextureFilter,
    mag_filter: GlTextureFilter,
    wrap_s: GlTextureWrap,
    wrap_t: GlTextureWrap | None,
    wrap_r: GlTextureWrap | None,
    wrap_color: FVector4,
    anisotropy: float,
    /,
) -> None: ...
def get_gl_shader_uniforms(shader: GlShader, /) -> tuple[tuple[str, int, GlType, int], ...]: ...
