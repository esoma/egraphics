from __future__ import annotations

__all__ = ["GBufferViewMap"]

# egraphics
from ._egraphics import GL_BYTE
from ._egraphics import GL_DOUBLE
from ._egraphics import GL_FLOAT
from ._egraphics import GL_INT
from ._egraphics import GL_SHORT
from ._egraphics import GL_UNSIGNED_BYTE
from ._egraphics import GL_UNSIGNED_INT
from ._egraphics import GL_UNSIGNED_SHORT
from ._egraphics import GlType
from ._egraphics import GlVertexArray
from ._egraphics import activate_gl_vertex_array
from ._egraphics import create_gl_vertex_array
from ._egraphics import delete_gl_vertex_array
from ._g_buffer import GBufferTarget
from ._g_buffer_view import GBufferView
from ._shader import Shader

# emath
import emath

# pyopengl
from OpenGL.GL import GL_FALSE
from OpenGL.GL import glEnableVertexAttribArray
from OpenGL.GL import glVertexAttribDivisor
from OpenGL.GL import glVertexAttribPointer

# python
from collections.abc import Mapping
from collections.abc import Set
import ctypes
from ctypes import c_void_p
from typing import Any
from typing import ClassVar
from typing import Final
from weakref import WeakKeyDictionary
from weakref import ref

IndexGBufferView = (
    GBufferView[ctypes.c_uint8] | GBufferView[ctypes.c_uint16] | GBufferView[ctypes.c_uint32]
)


class GBufferViewMap:
    def __init__(
        self,
        mapping: Mapping[str, GBufferView],
        indices: tuple[int, int] | IndexGBufferView,
        /,
    ) -> None:
        if isinstance(indices, GBufferView):
            if indices.stride != indices.data_type_size:
                raise ValueError(
                    "view buffer with a stride different from its type cannot be used "
                    "for indexing"
                )
            if indices.offset != 0:
                raise ValueError(
                    "view buffer with an offset other than 0 cannot be used for " "indexing"
                )
            if indices.instancing_divisor is not None:
                raise ValueError("view buffer with instancing_divisor cannot be used for indexing")
            if indices.data_type not in _INDEX_BUFFER_TYPES:
                raise ValueError(
                    f"view buffer with type {indices.data_type} cannot be used for indexing"
                )

        self._mapping = dict(mapping)
        self._shader_mapping: WeakKeyDictionary[Shader, _GlVertexArray] = WeakKeyDictionary()
        self._indices = indices

    def __len__(self) -> int:
        return len(self._mapping)

    def __getitem__(self, key: str) -> GBufferView:
        return self._mapping[key]

    def _get_gl_vertex_array_for_shader(self, shader: Shader) -> _GlVertexArray:
        try:
            return self._shader_mapping[shader]
        except (TypeError, KeyError):
            pass
        gl_vertex_array = self._shader_mapping[shader] = _GlVertexArray(
            shader, self._mapping, None if isinstance(self._indices, tuple) else self._indices
        )
        return gl_vertex_array

    def activate_for_shader(self, shader: Shader) -> None:
        gl_vertex_array = self._get_gl_vertex_array_for_shader(shader)
        gl_vertex_array._activate()

    @property
    def indices(self) -> tuple[int, int] | IndexGBufferView:
        return self._indices


class _GlVertexArray:
    _active: ClassVar[ref[_GlVertexArray] | None] = None

    _gl_vertex_array: GlVertexArray | None

    def __init__(
        self,
        shader: Shader,
        mapping: Mapping[str, GBufferView],
        index_g_buffer_view: IndexGBufferView | None,
    ) -> None:
        self._gl_vertex_array = create_gl_vertex_array()
        self._activate()

        if index_g_buffer_view is not None:
            GBufferTarget.ELEMENT_ARRAY.g_buffer = index_g_buffer_view.g_buffer

        attributes = shader.attributes
        attribute_names = {a.name for a in shader.attributes}

        for name in mapping:
            if name not in attribute_names:
                raise ValueError(f'shader does not accept an attribute called "{name}"')

        for attribute in shader.attributes:
            try:
                buffer_view = mapping[attribute.name]
            except KeyError:
                raise ValueError(f"missing attribute: {attribute.name}")

            GBufferTarget.ARRAY.g_buffer = buffer_view.g_buffer
            attr_gl_type = (_BUFFER_VIEW_TYPE_TO_VERTEX_ATTRIB_POINTER[attribute.data_type])[0]
            view_gl_type, count, locations = _BUFFER_VIEW_TYPE_TO_VERTEX_ATTRIB_POINTER[
                buffer_view.data_type
            ]
            for location_offset in range(locations):
                location = attribute.location + location_offset
                offset = buffer_view.offset + ((buffer_view.stride // locations) * location_offset)
                """
                if attr_gl_type == GL_DOUBLE and view_gl_type == GL_DOUBLE:
                    glVertexAttribLPointer(
                        location, count, view_gl_type, buffer_view.stride, c_void_p(offset)
                    )
                elif attr_gl_type in _GL_INT_TYPES and view_gl_type in _GL_INT_TYPES:
                    glVertexAttribIPointer(
                        location, count, view_gl_type, buffer_view.stride, c_void_p(offset)
                    )
                else:
                """
                glVertexAttribPointer(
                    location,
                    count,
                    view_gl_type,
                    GL_FALSE,
                    buffer_view.stride,
                    c_void_p(offset),
                )
                glEnableVertexAttribArray(location)
                if buffer_view.instancing_divisor is not None:
                    glVertexAttribDivisor(location, buffer_view.instancing_divisor)

    def _activate(self) -> None:
        if self._active and self._active() is self:
            return
        activate_gl_vertex_array(self._gl_vertex_array)
        _GlVertexArray._active = ref(self)

    def __del__(self) -> None:
        if self._gl_vertex_array:
            if self._active and self._active() is self:
                activate_gl_vertex_array(None)
                _GlVertexArray._active = None
            delete_gl_vertex_array(self._gl_vertex_array)
            self._gl_vertex_array = None


_BUFFER_VIEW_TYPE_TO_VERTEX_ATTRIB_POINTER: Final[Mapping[Any, tuple[GlType, int, int]]] = {
    ctypes.c_float: (GL_FLOAT, 1, 1),
    ctypes.c_double: (GL_DOUBLE, 1, 1),
    ctypes.c_int8: (GL_BYTE, 1, 1),
    ctypes.c_uint8: (GL_UNSIGNED_BYTE, 1, 1),
    ctypes.c_int16: (GL_SHORT, 1, 1),
    ctypes.c_uint16: (GL_UNSIGNED_SHORT, 1, 1),
    ctypes.c_int32: (GL_INT, 1, 1),
    ctypes.c_uint32: (GL_UNSIGNED_INT, 1, 1),
    emath.FVector2: (GL_FLOAT, 2, 1),
    emath.DVector2: (GL_DOUBLE, 2, 1),
    emath.I8Vector2: (GL_BYTE, 2, 1),
    emath.I16Vector2: (GL_SHORT, 2, 1),
    emath.I32Vector2: (GL_INT, 2, 1),
    emath.U8Vector2: (GL_UNSIGNED_BYTE, 2, 1),
    emath.U16Vector2: (GL_UNSIGNED_SHORT, 2, 1),
    emath.U32Vector2: (GL_UNSIGNED_INT, 2, 1),
    emath.FVector3: (GL_FLOAT, 3, 1),
    emath.DVector3: (GL_DOUBLE, 3, 1),
    emath.I8Vector3: (GL_BYTE, 3, 1),
    emath.I16Vector3: (GL_SHORT, 3, 1),
    emath.I32Vector3: (GL_INT, 3, 1),
    emath.U8Vector3: (GL_UNSIGNED_BYTE, 3, 1),
    emath.U16Vector3: (GL_UNSIGNED_SHORT, 3, 1),
    emath.U32Vector3: (GL_UNSIGNED_INT, 3, 1),
    emath.FVector4: (GL_FLOAT, 4, 1),
    emath.DVector4: (GL_DOUBLE, 4, 1),
    emath.I8Vector4: (GL_BYTE, 4, 1),
    emath.I16Vector4: (GL_SHORT, 4, 1),
    emath.I32Vector4: (GL_INT, 4, 1),
    emath.U8Vector4: (GL_UNSIGNED_BYTE, 4, 1),
    emath.U16Vector4: (GL_UNSIGNED_SHORT, 4, 1),
    emath.U32Vector4: (GL_UNSIGNED_INT, 4, 1),
    emath.FMatrix2x2: (GL_FLOAT, 2, 2),
    emath.DMatrix2x2: (GL_DOUBLE, 2, 2),
    emath.FMatrix2x3: (GL_FLOAT, 2, 3),
    emath.DMatrix2x3: (GL_DOUBLE, 2, 3),
    emath.FMatrix2x4: (GL_FLOAT, 2, 4),
    emath.DMatrix2x4: (GL_DOUBLE, 2, 4),
    emath.FMatrix3x2: (GL_FLOAT, 3, 2),
    emath.DMatrix3x2: (GL_DOUBLE, 3, 2),
    emath.FMatrix3x3: (GL_FLOAT, 3, 3),
    emath.DMatrix3x3: (GL_DOUBLE, 3, 3),
    emath.FMatrix3x4: (GL_FLOAT, 3, 4),
    emath.DMatrix3x4: (GL_DOUBLE, 3, 4),
    emath.FMatrix4x2: (GL_FLOAT, 4, 2),
    emath.DMatrix4x2: (GL_DOUBLE, 4, 2),
    emath.FMatrix4x3: (GL_FLOAT, 4, 3),
    emath.DMatrix4x3: (GL_DOUBLE, 4, 3),
    emath.FMatrix4x4: (GL_FLOAT, 4, 4),
    emath.DMatrix4x4: (GL_DOUBLE, 4, 4),
}

_INDEX_BUFFER_TYPES: Final[Set] = {ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32}
