from __future__ import annotations

__all__ = [
    "BlendFactor",
    "BlendFunction",
    "DepthTest",
    "FaceCull",
    "PrimitiveMode",
    "Shader",
    "ShaderAttribute",
    "ShaderUniform",
    "UniformMap",
]


# egraphics
from ._egraphics import GL_ALWAYS
from ._egraphics import GL_BACK
from ._egraphics import GL_BOOL
from ._egraphics import GL_CONSTANT_ALPHA
from ._egraphics import GL_CONSTANT_COLOR
from ._egraphics import GL_DOUBLE
from ._egraphics import GL_DOUBLE_MAT2
from ._egraphics import GL_DOUBLE_MAT2x3
from ._egraphics import GL_DOUBLE_MAT2x4
from ._egraphics import GL_DOUBLE_MAT3
from ._egraphics import GL_DOUBLE_MAT3x2
from ._egraphics import GL_DOUBLE_MAT3x4
from ._egraphics import GL_DOUBLE_MAT4
from ._egraphics import GL_DOUBLE_MAT4x2
from ._egraphics import GL_DOUBLE_MAT4x3
from ._egraphics import GL_DOUBLE_VEC2
from ._egraphics import GL_DOUBLE_VEC3
from ._egraphics import GL_DOUBLE_VEC4
from ._egraphics import GL_DST_ALPHA
from ._egraphics import GL_DST_COLOR
from ._egraphics import GL_EQUAL
from ._egraphics import GL_FLOAT
from ._egraphics import GL_FLOAT_MAT2
from ._egraphics import GL_FLOAT_MAT2x3
from ._egraphics import GL_FLOAT_MAT2x4
from ._egraphics import GL_FLOAT_MAT3
from ._egraphics import GL_FLOAT_MAT3x2
from ._egraphics import GL_FLOAT_MAT3x4
from ._egraphics import GL_FLOAT_MAT4
from ._egraphics import GL_FLOAT_MAT4x2
from ._egraphics import GL_FLOAT_MAT4x3
from ._egraphics import GL_FLOAT_VEC2
from ._egraphics import GL_FLOAT_VEC3
from ._egraphics import GL_FLOAT_VEC4
from ._egraphics import GL_FRONT
from ._egraphics import GL_FUNC_ADD
from ._egraphics import GL_FUNC_REVERSE_SUBTRACT
from ._egraphics import GL_FUNC_SUBTRACT
from ._egraphics import GL_GEQUAL
from ._egraphics import GL_GREATER
from ._egraphics import GL_INT
from ._egraphics import GL_INT_SAMPLER_1D
from ._egraphics import GL_INT_SAMPLER_1D_ARRAY
from ._egraphics import GL_INT_SAMPLER_2D
from ._egraphics import GL_INT_SAMPLER_2D_ARRAY
from ._egraphics import GL_INT_SAMPLER_2D_MULTISAMPLE
from ._egraphics import GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY
from ._egraphics import GL_INT_SAMPLER_2D_RECT
from ._egraphics import GL_INT_SAMPLER_3D
from ._egraphics import GL_INT_SAMPLER_BUFFER
from ._egraphics import GL_INT_SAMPLER_CUBE
from ._egraphics import GL_INT_SAMPLER_CUBE_MAP_ARRAY
from ._egraphics import GL_INT_VEC2
from ._egraphics import GL_INT_VEC3
from ._egraphics import GL_INT_VEC4
from ._egraphics import GL_LEQUAL
from ._egraphics import GL_LESS
from ._egraphics import GL_LINES
from ._egraphics import GL_LINE_LOOP
from ._egraphics import GL_LINE_STRIP
from ._egraphics import GL_MAX
from ._egraphics import GL_MIN
from ._egraphics import GL_NEVER
from ._egraphics import GL_NOTEQUAL
from ._egraphics import GL_ONE
from ._egraphics import GL_ONE_MINUS_CONSTANT_ALPHA
from ._egraphics import GL_ONE_MINUS_CONSTANT_COLOR
from ._egraphics import GL_ONE_MINUS_DST_ALPHA
from ._egraphics import GL_ONE_MINUS_DST_COLOR
from ._egraphics import GL_ONE_MINUS_SRC_ALPHA
from ._egraphics import GL_ONE_MINUS_SRC_COLOR
from ._egraphics import GL_POINTS
from ._egraphics import GL_SAMPLER_1D
from ._egraphics import GL_SAMPLER_1D_ARRAY
from ._egraphics import GL_SAMPLER_1D_ARRAY_SHADOW
from ._egraphics import GL_SAMPLER_1D_SHADOW
from ._egraphics import GL_SAMPLER_2D
from ._egraphics import GL_SAMPLER_2D_ARRAY
from ._egraphics import GL_SAMPLER_2D_ARRAY_SHADOW
from ._egraphics import GL_SAMPLER_2D_MULTISAMPLE
from ._egraphics import GL_SAMPLER_2D_MULTISAMPLE_ARRAY
from ._egraphics import GL_SAMPLER_2D_RECT
from ._egraphics import GL_SAMPLER_2D_RECT_SHADOW
from ._egraphics import GL_SAMPLER_2D_SHADOW
from ._egraphics import GL_SAMPLER_3D
from ._egraphics import GL_SAMPLER_BUFFER
from ._egraphics import GL_SAMPLER_CUBE
from ._egraphics import GL_SAMPLER_CUBE_MAP_ARRAY
from ._egraphics import GL_SAMPLER_CUBE_SHADOW
from ._egraphics import GL_SRC_ALPHA
from ._egraphics import GL_SRC_COLOR
from ._egraphics import GL_TRIANGLES
from ._egraphics import GL_TRIANGLE_FAN
from ._egraphics import GL_TRIANGLE_STRIP
from ._egraphics import GL_UNSIGNED_BYTE
from ._egraphics import GL_UNSIGNED_INT
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_1D
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_1D_ARRAY
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_2D
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_2D_ARRAY
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_2D_RECT
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_3D
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_BUFFER
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_CUBE
from ._egraphics import GL_UNSIGNED_INT_SAMPLER_CUBE_MAP_ARRAY
from ._egraphics import GL_UNSIGNED_INT_VEC2
from ._egraphics import GL_UNSIGNED_INT_VEC3
from ._egraphics import GL_UNSIGNED_INT_VEC4
from ._egraphics import GL_UNSIGNED_SHORT
from ._egraphics import GL_ZERO
from ._egraphics import GlType
from ._egraphics import get_gl_shader_uniforms
from ._g_buffer_view import GBufferView
from ._texture import Texture

# emath
import emath
from emath import FVector4
from emath import I32Array

# eplatform
from eplatform import Platform
from eplatform import RenderTarget
from eplatform import set_draw_render_target

# pyopengl
import OpenGL.GL
from OpenGL.GL import GL_ACTIVE_ATTRIBUTES
from OpenGL.GL import GL_BLEND
from OpenGL.GL import GL_COMPILE_STATUS
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_GEOMETRY_SHADER
from OpenGL.GL import GL_LINK_STATUS
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glAttachShader
from OpenGL.GL import glBlendColor
from OpenGL.GL import glBlendEquation
from OpenGL.GL import glBlendFuncSeparate
from OpenGL.GL import glColorMask
from OpenGL.GL import glCompileShader
from OpenGL.GL import glCreateProgram
from OpenGL.GL import glCreateShader
from OpenGL.GL import glCullFace
from OpenGL.GL import glDeleteProgram
from OpenGL.GL import glDeleteShader
from OpenGL.GL import glDepthFunc
from OpenGL.GL import glDepthMask
from OpenGL.GL import glDisable
from OpenGL.GL import glDrawArrays
from OpenGL.GL import glDrawArraysInstanced
from OpenGL.GL import glDrawElements
from OpenGL.GL import glDrawElementsInstanced
from OpenGL.GL import glEnable
from OpenGL.GL import glGetActiveAttrib
from OpenGL.GL import glGetAttribLocation
from OpenGL.GL import glGetProgramInfoLog
from OpenGL.GL import glGetProgramiv
from OpenGL.GL import glGetShaderInfoLog
from OpenGL.GL import glGetShaderiv
from OpenGL.GL import glLinkProgram
from OpenGL.GL import glShaderSource
from OpenGL.GL import glUseProgram
from OpenGL.error import GLError
from OpenGL.error import NullFunctionError

# python
from collections.abc import Mapping
from collections.abc import Set
from contextlib import ExitStack
import ctypes
from ctypes import c_char_p
from ctypes import c_void_p
from ctypes import cast as c_cast
from enum import Enum
from typing import Any
from typing import BinaryIO
from typing import ClassVar
from typing import Final
from typing import Generic
from typing import Mapping
from typing import Sequence
from typing import TYPE_CHECKING
from typing import TypeVar
from weakref import ref

if TYPE_CHECKING:
    # egraphics
    from ._g_buffer_view_map import GBufferViewMap

_T = TypeVar("_T")


class DepthTest(Enum):
    NEVER = GL_NEVER
    ALWAYS = GL_ALWAYS
    LESS = GL_LESS
    LESS_EQUAL = GL_LEQUAL
    GREATER = GL_GREATER
    GREATER_EQUAL = GL_GEQUAL
    EQUAL = GL_EQUAL
    NOT_EQUAL = GL_NOTEQUAL


class BlendFactor(Enum):
    ZERO = GL_ZERO
    ONE = GL_ONE
    SOURCE_COLOR = GL_SRC_COLOR
    ONE_MINUS_SOURCE_COLOR = GL_ONE_MINUS_SRC_COLOR
    DESTINATION_COLOR = GL_DST_COLOR
    ONE_MINUS_DESTINATION_COLOR = GL_ONE_MINUS_DST_COLOR
    SOURCE_ALPHA = GL_SRC_ALPHA
    ONE_MINUS_SOURCE_ALPHA = GL_ONE_MINUS_SRC_ALPHA
    DESTINATION_ALPHA = GL_DST_ALPHA
    ONE_MINUS_DESTINATION_ALPHA = GL_ONE_MINUS_DST_ALPHA
    BLEND_COLOR = GL_CONSTANT_COLOR
    ONE_MINUS_BLEND_COLOR = GL_ONE_MINUS_CONSTANT_COLOR
    BLEND_ALPHA = GL_CONSTANT_ALPHA
    ONE_MINUS_BLEND_ALPHA = GL_ONE_MINUS_CONSTANT_ALPHA


class BlendFunction(Enum):
    ADD = GL_FUNC_ADD
    SUBTRACT = GL_FUNC_SUBTRACT
    SUBTRACT_REVERSED = GL_FUNC_REVERSE_SUBTRACT
    MIN = GL_MIN
    MAX = GL_MAX


class FaceCull(Enum):
    NONE = 0
    FRONT = GL_FRONT
    BACK = GL_BACK


class Shader:
    _active: ClassVar[ref[Shader] | None] = None
    _color_mask: ClassVar[tuple[bool, bool, bool, bool]] = (True, True, True, True)
    _depth_test: ClassVar[bool] = False
    _depth_mask: ClassVar[bool] = True
    _depth_func: ClassVar[DepthTest] = DepthTest.LESS
    _blend: ClassVar[bool] = False
    _blend_factors: ClassVar[tuple[BlendFactor, BlendFactor, BlendFactor, BlendFactor]] = (
        BlendFactor.ONE,
        BlendFactor.ZERO,
        BlendFactor.ONE,
        BlendFactor.ZERO,
    )
    _blend_equation: ClassVar[BlendFunction] = BlendFunction.ADD
    _blend_color: FVector4 = FVector4(0)
    _face_cull: FaceCull = FaceCull.NONE

    def __init__(
        self,
        *,
        vertex: BinaryIO | None = None,
        geometry: BinaryIO | None = None,
        fragment: BinaryIO | None = None,
    ):
        if vertex is None and geometry is None and fragment is None:
            raise TypeError("vertex, geometry or fragment must be provided")

        if geometry is not None and vertex is None:
            raise TypeError("geometry shader requires vertex shader")

        stages: list[int] = []

        def add_stage(name: str, file: BinaryIO, type: int) -> None:
            gl = glCreateShader(type)
            stages.append(gl)
            glShaderSource(gl, file.read())
            glCompileShader(gl)
            if not glGetShaderiv(gl, GL_COMPILE_STATUS):
                raise RuntimeError(
                    f"{name} stage failed to compile:\n" + glGetShaderInfoLog(gl).decode("utf8")
                )

        try:
            if vertex is not None:
                add_stage("vertex", vertex, GL_VERTEX_SHADER)
            if geometry is not None:
                add_stage("geometry", geometry, GL_GEOMETRY_SHADER)
            if fragment is not None:
                add_stage("fragment", fragment, GL_FRAGMENT_SHADER)

            self._gl_shader = glCreateProgram()
            for stage in stages:
                glAttachShader(self._gl_shader, stage)
            glLinkProgram(self._gl_shader)

            if glGetProgramiv(self._gl_shader, GL_LINK_STATUS) == GL_FALSE:
                raise RuntimeError(
                    "Failed to link:\n" + glGetProgramInfoLog(self._gl_shader).decode("utf8")
                )
        finally:
            for stage in stages:
                glDeleteShader(stage)

        attributes: list[ShaderAttribute] = []
        attribute_count = glGetProgramiv(self._gl_shader, GL_ACTIVE_ATTRIBUTES)
        for i in range(attribute_count):
            c_name, size, type = glGetActiveAttrib(self._gl_shader, i)
            name = c_cast(c_name, c_char_p).value.decode("utf8")  # type: ignore
            location = glGetAttribLocation(self._gl_shader, name)
            attributes.append(
                ShaderAttribute(
                    name.removesuffix("[0]"),
                    _GL_TYPE_TO_PY[type],
                    size,
                    location,
                )
            )
        self._attributes = tuple(attributes)

        self._uniforms = tuple(
            ShaderUniform(
                name.removesuffix("[0]"),
                _GL_TYPE_TO_PY[type],
                size,
                location,
            )
            for name, size, type, location in get_gl_shader_uniforms(self._gl_shader)
        )

        self._inputs: dict[str, ShaderAttribute | ShaderUniform] = {
            **{attribute.name: attribute for attribute in attributes},
            **{uniform.name: uniform for uniform in self._uniforms},
        }

    def __del__(self) -> None:
        if self._active and self._active() is self:
            glUseProgram(0)
            Shader._active = None
        if hasattr(self, "_gl_shader") and self._gl_shader is not None:
            try:
                glDeleteProgram(self._gl_shader)
            except (TypeError, NullFunctionError, GLError):
                pass
            self._gl_shader = None

    def __getitem__(self, name: str) -> ShaderAttribute | ShaderUniform:
        return self._inputs[name]

    def _set_uniform(
        self,
        uniform: ShaderUniform,
        value: UniformValue,
        exit_stack: ExitStack,
    ) -> None:
        assert uniform in self._uniforms
        input_value: Any = None
        cache_key: Any = value
        if uniform.data_type is Texture:
            if uniform.size > 1:
                try:
                    length = len(value)  # type: ignore
                except TypeError:
                    raise ValueError(
                        f"expected sequence of {Texture} for {uniform.name} "
                        f"(got {type(value)})"
                    )
                if length != uniform.size:
                    raise ValueError(
                        f"expected sequence of length {uniform.size} "
                        f"for {uniform.name} "
                        f"(got sequence of length {length})"
                    )
                for v in value:  # type: ignore
                    if not isinstance(v, Texture):
                        raise ValueError(
                            f"expected sequence of {Texture} for {uniform.name} "
                            f"(got {value!r})"
                        )
                value = I32Array(
                    *(exit_stack.enter_context(v.bind_unit()) for v in value)  # type: ignore
                )
                input_value = value.pointer
            else:
                if not isinstance(value, Texture):
                    raise ValueError(
                        f"expected {Texture} for {uniform.name} " f"(got {type(value)})"
                    )
                input_value = exit_stack.enter_context(value.bind_unit())
        else:
            if uniform.size > 1:
                array_type = _PY_TYPE_TO_ARRAY[uniform.data_type]
                if not isinstance(value, array_type):
                    raise ValueError(
                        f"expected {array_type} for {uniform.name} " f"(got {type(value)})"
                    )
                if len(value) != uniform.size:
                    raise ValueError(
                        f"expected array of length {uniform.size} "
                        f"for {uniform.name} "
                        f"(got array of length {len(value)})"
                    )
                input_value = value.pointer
            else:
                assert uniform.size == 1
                if not isinstance(value, uniform._set_type):
                    raise ValueError(
                        f"expected {uniform._set_type} for {uniform.name} " f"(got {type(value)})"
                    )
                if uniform._set_type in _POD_UNIFORM_TYPES:
                    input_value = value.value
                    cache_key = value.value
                else:
                    input_value = value.pointer
        uniform._set(uniform.location, uniform.size, input_value, cache_key)

    @property
    def attributes(self) -> tuple[ShaderAttribute, ...]:
        return self._attributes

    @property
    def uniforms(self) -> tuple[ShaderUniform, ...]:
        return self._uniforms

    @staticmethod
    def _set_color_mask(mask: tuple[bool, bool, bool, bool]) -> None:
        if Shader._color_mask != mask:
            glColorMask(*mask)
            Shader._color_mask = mask

    @staticmethod
    def _set_depth_test(test: bool) -> None:
        if Shader._depth_test == test:
            return
        if test:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)
        Shader._depth_test = test

    @staticmethod
    def _set_depth_mask(mask: bool) -> None:
        if Shader._depth_mask == mask:
            return
        glDepthMask(mask)
        Shader._depth_mask = mask

    @staticmethod
    def _set_depth_func(func: DepthTest) -> None:
        if Shader._depth_func == func:
            return
        glDepthFunc(func.value)
        Shader._depth_func = func

    @staticmethod
    def _set_blend(blend: bool) -> None:
        if Shader._blend == blend:
            return
        if blend:
            glEnable(GL_BLEND)
        else:
            glDisable(GL_BLEND)
        Shader._blend = blend

    @staticmethod
    def _set_blend_factors(
        blend_source: BlendFactor,
        blend_destination: BlendFactor,
        blend_source_alpha: BlendFactor,
        blend_destination_alpha: BlendFactor,
    ) -> None:
        factors = (blend_source, blend_destination, blend_source_alpha, blend_destination_alpha)
        if Shader._blend_factors == factors:
            return
        glBlendFuncSeparate(
            blend_source.value,
            blend_destination.value,
            blend_source_alpha.value,
            blend_destination_alpha.value,
        )
        Shader._blend_factors = factors

    @staticmethod
    def _set_blend_equation(equation: BlendFunction) -> None:
        if Shader._blend_equation == equation:
            return
        glBlendEquation(equation.value)
        Shader._blend_equation = equation

    @staticmethod
    def _set_blend_color(color: FVector4) -> None:
        if Shader._blend_color == color:
            return
        glBlendColor(*color)
        Shader._blend_color = color

    @staticmethod
    def _set_face_cull(face_cull: FaceCull) -> None:
        if Shader._face_cull == face_cull:
            return
        if face_cull == FaceCull.NONE:
            glDisable(GL_CULL_FACE)
        else:
            glEnable(GL_CULL_FACE)
            glCullFace(face_cull.value)
        Shader._face_cull = face_cull

    def _activate(self) -> None:
        if self._active and self._active() is self:
            return
        glUseProgram(self._gl_shader)
        Shader._active = ref(self)

    def execute(
        self,
        render_target: RenderTarget,
        primitive_mode: PrimitiveMode,
        buffer_view_map: GBufferViewMap,
        uniforms: UniformMap,
        *,
        blend_source: BlendFactor = BlendFactor.ONE,
        blend_destination: BlendFactor = BlendFactor.ZERO,
        blend_source_alpha: BlendFactor | None = None,
        blend_destination_alpha: BlendFactor | None = None,
        blend_function: BlendFunction = BlendFunction.ADD,
        blend_color: FVector4 | None = None,
        color_write: tuple[bool, bool, bool, bool] = (True, True, True, True),
        depth_test: DepthTest = DepthTest.ALWAYS,
        depth_write: bool = False,
        face_cull: FaceCull = FaceCull.NONE,
        instances: int = 1,
    ) -> None:
        for uniform_name in uniforms:
            try:
                input = self[uniform_name]
            except KeyError:
                raise ValueError(f'shader does not accept a uniform called "{uniform_name}"')
            if not isinstance(input, ShaderUniform):
                raise ValueError(f'shader does not accept a uniform called "{uniform_name}"')
        uniform_values: list[tuple[ShaderUniform, Any]] = []
        for uniform in self.uniforms:
            try:
                value = uniforms[uniform.name]
            except KeyError:
                raise ValueError(f"missing uniform: {uniform.name}")
            uniform_values.append((uniform, value))
        if instances < 0:
            raise ValueError("instances must be 0 or more")
        elif instances == 0:
            return

        if not depth_write and depth_test == DepthTest.ALWAYS:
            self._set_depth_test(False)
        else:
            self._set_depth_test(True)
            self._set_depth_mask(depth_write)
            self._set_depth_func(depth_test)

        self._set_color_mask(color_write)

        if blend_source_alpha is None:
            blend_source_alpha = blend_source
        if blend_destination_alpha is None:
            blend_destination_alpha = blend_destination
        if blend_color is None:
            blend_color = FVector4(1)

        if (
            blend_source == BlendFactor.ONE
            and blend_source_alpha == BlendFactor.ONE
            and blend_destination == BlendFactor.ZERO
            and blend_destination_alpha == BlendFactor.ZERO
        ):
            self._set_blend(False)
        else:
            self._set_blend(True)
            self._set_blend_factors(
                blend_source, blend_destination, blend_source_alpha, blend_destination_alpha
            )
            self._set_blend_equation(blend_function)
            self._set_blend_color(blend_color)

        self._set_face_cull(face_cull)

        set_draw_render_target(render_target)
        self._activate()

        with ExitStack() as exit_stack:
            for uniform, value in uniform_values:
                self._set_uniform(uniform, value, exit_stack)
            buffer_view_map.activate_for_shader(self)

            if isinstance(buffer_view_map.indices, GBufferView):
                index_gl_type = _INDEX_BUFFER_VIEW_TYPE_TO_VERTEX_ATTRIB_POINTER[
                    buffer_view_map.indices.data_type
                ]
                if instances > 1:
                    glDrawElementsInstanced(
                        primitive_mode.value,
                        len(buffer_view_map.indices),
                        index_gl_type,
                        c_void_p(0),
                        instances,
                    )
                else:
                    glDrawElements(
                        primitive_mode.value,
                        len(buffer_view_map.indices),
                        index_gl_type,
                        c_void_p(0),
                    )
            else:
                index_range = buffer_view_map.indices
                if instances > 1:
                    glDrawArraysInstanced(
                        primitive_mode.value, index_range[0], index_range[1], instances
                    )
                else:
                    glDrawArrays(primitive_mode.value, index_range[0], index_range[1])


@Platform.register_deactivate_callback
def _reset_shader_state() -> None:
    Shader._active = None
    Shader._color_mask = (True, True, True, True)
    Shader._depth_test = False
    Shader._depth_mask = True
    Shader._depth_func = DepthTest.LESS
    Shader._blend = False
    Shader._blend_factors = (BlendFactor.ONE, BlendFactor.ZERO, BlendFactor.ONE, BlendFactor.ZERO)
    Shader._blend_equation = BlendFunction.ADD
    Shader._blend_color = FVector4(0)
    Shader._face_cull = FaceCull.NONE


class ShaderAttribute(Generic[_T]):
    def __init__(self, name: str, data_type: type[_T], size: int, location: int) -> None:
        self._name = name
        self._data_type: type[_T] = data_type
        self._size = size
        self._location = location

    def __repr__(self) -> str:
        return f"<ShaderAttribute {self.name!r}>"

    @property
    def name(self) -> str:
        return self._name

    @property
    def data_type(self) -> type[_T]:
        return self._data_type

    @property
    def size(self) -> int:
        return self._size

    @property
    def location(self) -> int:
        return self._location


class ShaderUniform(Generic[_T]):
    def __init__(self, name: str, data_type: type[_T], size: int, location: int) -> None:
        self._name = name
        self._data_type: type[_T] = data_type
        self._size = size
        self._location = location
        self._setter = _TYPE_TO_UNIFORM_SETTER[data_type]
        self._set_type: Any = ctypes.c_int32 if data_type is Texture else data_type
        self._cache: Any = None

    def __repr__(self) -> str:
        return f"<ShaderUniform {self.name!r}>"

    def _set(self, location: int, size: int, gl_value: Any, cache_key: Any) -> None:
        if self._cache == cache_key:
            return
        self._setter(location, size, gl_value)
        self._cache = cache_key

    @property
    def name(self) -> str:
        return self._name

    @property
    def data_type(self) -> type[_T]:
        return self._data_type

    @property
    def size(self) -> int:
        return self._size

    @property
    def location(self) -> int:
        return self._location


def _wrap_uniform_matrix(f: Any) -> Any:
    def _(location: Any, count: Any, value: Any) -> None:
        f(location, count, GL_FALSE, value)

    return _


_GL_TYPE_TO_PY: Final[Mapping[GlType, Any]] = {
    GL_FLOAT: ctypes.c_float,
    GL_FLOAT_VEC2: emath.FVector2,
    GL_FLOAT_VEC3: emath.FVector3,
    GL_FLOAT_VEC4: emath.FVector4,
    GL_DOUBLE: ctypes.c_double,
    GL_DOUBLE_VEC2: emath.DVector2,
    GL_DOUBLE_VEC3: emath.DVector3,
    GL_DOUBLE_VEC4: emath.DVector4,
    GL_INT: ctypes.c_int32,
    GL_INT_VEC2: emath.I32Vector2,
    GL_INT_VEC3: emath.I32Vector3,
    GL_INT_VEC4: emath.I32Vector4,
    GL_UNSIGNED_INT: ctypes.c_uint32,
    GL_UNSIGNED_INT_VEC2: emath.U32Vector2,
    GL_UNSIGNED_INT_VEC3: emath.U32Vector3,
    GL_UNSIGNED_INT_VEC4: emath.U32Vector4,
    GL_BOOL: ctypes.c_bool,
    GL_FLOAT_MAT2: emath.FMatrix2x2,
    GL_FLOAT_MAT3: emath.FMatrix3x3,
    GL_FLOAT_MAT4: emath.FMatrix4x4,
    GL_FLOAT_MAT2x3: emath.FMatrix2x3,
    GL_FLOAT_MAT2x4: emath.FMatrix2x4,
    GL_FLOAT_MAT3x2: emath.FMatrix3x2,
    GL_FLOAT_MAT3x4: emath.FMatrix3x4,
    GL_FLOAT_MAT4x2: emath.FMatrix4x2,
    GL_FLOAT_MAT4x3: emath.FMatrix4x3,
    GL_DOUBLE_MAT2: emath.DMatrix2x2,
    GL_DOUBLE_MAT3: emath.DMatrix3x3,
    GL_DOUBLE_MAT4: emath.DMatrix4x4,
    GL_DOUBLE_MAT2x3: emath.DMatrix2x3,
    GL_DOUBLE_MAT2x4: emath.DMatrix2x4,
    GL_DOUBLE_MAT3x2: emath.DMatrix3x2,
    GL_DOUBLE_MAT3x4: emath.DMatrix3x4,
    GL_DOUBLE_MAT4x2: emath.DMatrix4x2,
    GL_DOUBLE_MAT4x3: emath.DMatrix4x3,
    GL_SAMPLER_1D: Texture,
    GL_INT_SAMPLER_1D: Texture,
    GL_UNSIGNED_INT_SAMPLER_1D: Texture,
    GL_SAMPLER_2D: Texture,
    GL_INT_SAMPLER_2D: Texture,
    GL_UNSIGNED_INT_SAMPLER_2D: Texture,
    GL_SAMPLER_3D: Texture,
    GL_INT_SAMPLER_3D: Texture,
    GL_UNSIGNED_INT_SAMPLER_3D: Texture,
    GL_SAMPLER_CUBE: Texture,
    GL_INT_SAMPLER_CUBE: Texture,
    GL_UNSIGNED_INT_SAMPLER_CUBE: Texture,
    GL_SAMPLER_2D_RECT: Texture,
    GL_INT_SAMPLER_2D_RECT: Texture,
    GL_UNSIGNED_INT_SAMPLER_2D_RECT: Texture,
    GL_SAMPLER_1D_ARRAY: Texture,
    GL_INT_SAMPLER_1D_ARRAY: Texture,
    GL_UNSIGNED_INT_SAMPLER_1D_ARRAY: Texture,
    GL_SAMPLER_2D_ARRAY: Texture,
    GL_INT_SAMPLER_2D_ARRAY: Texture,
    GL_UNSIGNED_INT_SAMPLER_2D_ARRAY: Texture,
    GL_SAMPLER_CUBE_MAP_ARRAY: Texture,
    GL_INT_SAMPLER_CUBE_MAP_ARRAY: Texture,
    GL_UNSIGNED_INT_SAMPLER_CUBE_MAP_ARRAY: Texture,
    GL_SAMPLER_BUFFER: Texture,
    GL_INT_SAMPLER_BUFFER: Texture,
    GL_UNSIGNED_INT_SAMPLER_BUFFER: Texture,
    GL_SAMPLER_2D_MULTISAMPLE: Texture,
    GL_INT_SAMPLER_2D_MULTISAMPLE: Texture,
    GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE: Texture,
    GL_SAMPLER_2D_MULTISAMPLE_ARRAY: Texture,
    GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY: Texture,
    GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY: Texture,
    GL_SAMPLER_1D_SHADOW: Texture,
    GL_SAMPLER_2D_SHADOW: Texture,
    GL_SAMPLER_CUBE_SHADOW: Texture,
    GL_SAMPLER_2D_RECT_SHADOW: Texture,
    GL_SAMPLER_1D_ARRAY_SHADOW: Texture,
    GL_SAMPLER_2D_ARRAY_SHADOW: Texture,
}


_TYPE_TO_UNIFORM_SETTER: Final[Mapping] = {
    ctypes.c_float: OpenGL.GL.glUniform1fv,
    emath.FVector2: OpenGL.GL.glUniform2fv,
    emath.FVector3: OpenGL.GL.glUniform3fv,
    emath.FVector4: OpenGL.GL.glUniform4fv,
    ctypes.c_double: OpenGL.GL.glUniform1dv,
    emath.DVector2: OpenGL.GL.glUniform2dv,
    emath.DVector3: OpenGL.GL.glUniform3dv,
    emath.DVector4: OpenGL.GL.glUniform4dv,
    ctypes.c_int32: OpenGL.GL.glUniform1iv,
    emath.I32Vector2: OpenGL.GL.glUniform2iv,
    emath.I32Vector3: OpenGL.GL.glUniform3iv,
    emath.I32Vector4: OpenGL.GL.glUniform4iv,
    ctypes.c_uint32: OpenGL.GL.glUniform1uiv,
    emath.U32Vector2: OpenGL.GL.glUniform2uiv,
    emath.U32Vector3: OpenGL.GL.glUniform3uiv,
    emath.U32Vector4: OpenGL.GL.glUniform4uiv,
    ctypes.c_bool: OpenGL.GL.glUniform1iv,
    emath.FMatrix2x2: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix2fv),
    emath.FMatrix2x3: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix2x3fv),
    emath.FMatrix2x4: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix2x4fv),
    emath.FMatrix3x2: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix3x2fv),
    emath.FMatrix3x3: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix3fv),
    emath.FMatrix3x4: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix3x4fv),
    emath.FMatrix4x2: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix4x2fv),
    emath.FMatrix4x3: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix4x3fv),
    emath.FMatrix4x4: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix4fv),
    emath.DMatrix2x2: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix2dv),
    emath.DMatrix2x3: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix2x3dv),
    emath.DMatrix2x4: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix2x4dv),
    emath.DMatrix3x2: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix3x2dv),
    emath.DMatrix3x3: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix3dv),
    emath.DMatrix3x4: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix3x4dv),
    emath.DMatrix4x2: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix4x2dv),
    emath.DMatrix4x3: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix4x3dv),
    emath.DMatrix4x4: _wrap_uniform_matrix(OpenGL.GL.glUniformMatrix4dv),
    Texture: OpenGL.GL.glUniform1iv,
}

_POD_UNIFORM_TYPES: Final[Set] = {
    ctypes.c_float,
    ctypes.c_double,
    ctypes.c_int32,
    ctypes.c_uint32,
    ctypes.c_bool,
}

_PY_TYPE_TO_ARRAY: Final[Mapping] = {
    ctypes.c_float: emath.FArray,
    emath.FVector2: emath.FVector2Array,
    emath.FVector3: emath.FVector3Array,
    emath.FVector4: emath.FVector4Array,
    ctypes.c_double: emath.DArray,
    emath.DVector2: emath.DVector2Array,
    emath.DVector3: emath.DVector3Array,
    emath.DVector4: emath.DVector4Array,
    ctypes.c_int32: emath.I32Array,
    emath.I32Vector2: emath.I32Vector2Array,
    emath.I32Vector3: emath.I32Vector3Array,
    emath.I32Vector4: emath.I32Vector4Array,
    ctypes.c_uint32: emath.U32Array,
    emath.U32Vector2: emath.U32Vector2Array,
    emath.U32Vector3: emath.U32Vector3Array,
    emath.U32Vector4: emath.U32Vector4Array,
    ctypes.c_bool: emath.BArray,
    emath.FMatrix2x2: emath.FMatrix2x2Array,
    emath.FMatrix3x3: emath.FMatrix3x3Array,
    emath.FMatrix4x4: emath.FMatrix4x4Array,
    emath.FMatrix2x3: emath.FMatrix2x3Array,
    emath.FMatrix2x4: emath.FMatrix2x4Array,
    emath.FMatrix3x2: emath.FMatrix3x2Array,
    emath.FMatrix3x4: emath.FMatrix3x4Array,
    emath.FMatrix4x2: emath.FMatrix4x2Array,
    emath.FMatrix4x3: emath.FMatrix4x3Array,
    emath.DMatrix2x2: emath.DMatrix2x2Array,
    emath.DMatrix3x3: emath.DMatrix3x3Array,
    emath.DMatrix4x4: emath.DMatrix4x4Array,
    emath.DMatrix2x3: emath.DMatrix2x3Array,
    emath.DMatrix2x4: emath.DMatrix2x4Array,
    emath.DMatrix3x2: emath.DMatrix3x2Array,
    emath.DMatrix3x4: emath.DMatrix3x4Array,
    emath.DMatrix4x2: emath.DMatrix4x2Array,
    emath.DMatrix4x3: emath.DMatrix4x3Array,
}


class PrimitiveMode(Enum):
    POINT = GL_POINTS
    LINE = GL_LINES
    LINE_STRIP = GL_LINE_STRIP
    LINE_LOOP = GL_LINE_LOOP
    TRIANGLE = GL_TRIANGLES
    TRIANGLE_STRIP = GL_TRIANGLE_STRIP
    TRIANGLE_FAN = GL_TRIANGLE_FAN


UniformValue = (
    ctypes.c_float
    | emath.FArray
    | emath.FVector2
    | emath.FVector2Array
    | emath.FVector3
    | emath.FVector3Array
    | emath.FVector4
    | emath.FVector4Array
    | ctypes.c_double
    | emath.DArray
    | emath.DVector2
    | emath.DVector2Array
    | emath.DVector3
    | emath.DVector3Array
    | emath.DVector4
    | emath.DVector4Array
    | ctypes.c_int32
    | emath.I32Array
    | emath.I32Vector2
    | emath.I32Vector2Array
    | emath.I32Vector3
    | emath.I32Vector3Array
    | emath.I32Vector4
    | emath.I32Vector4Array
    | ctypes.c_uint32
    | emath.U32Array
    | emath.U32Vector2
    | emath.U32Vector2Array
    | emath.U32Vector3
    | emath.U32Vector3Array
    | emath.U32Vector4
    | emath.U32Vector4Array
    | ctypes.c_bool
    | emath.FMatrix2x2
    | emath.FMatrix2x2Array
    | emath.FMatrix2x3
    | emath.FMatrix2x3Array
    | emath.FMatrix2x4
    | emath.FMatrix2x4Array
    | emath.FMatrix3x2
    | emath.FMatrix3x2Array
    | emath.FMatrix3x3
    | emath.FMatrix3x3Array
    | emath.FMatrix3x4
    | emath.FMatrix3x4Array
    | emath.FMatrix4x2
    | emath.FMatrix4x2Array
    | emath.FMatrix4x3
    | emath.FMatrix4x3Array
    | emath.FMatrix4x4
    | emath.FMatrix4x4Array
    | emath.DMatrix2x2
    | emath.DMatrix2x2Array
    | emath.DMatrix2x3
    | emath.DMatrix2x3Array
    | emath.DMatrix2x4
    | emath.DMatrix2x4Array
    | emath.DMatrix3x2
    | emath.DMatrix3x2Array
    | emath.DMatrix3x3
    | emath.DMatrix3x3Array
    | emath.DMatrix3x4
    | emath.DMatrix3x4Array
    | emath.DMatrix4x2
    | emath.DMatrix4x2Array
    | emath.DMatrix4x3
    | emath.DMatrix4x3Array
    | emath.DMatrix4x4
    | emath.DMatrix4x4Array
    | Texture
    | Sequence[Texture]
)

UniformMap = Mapping[str, UniformValue]

_INDEX_BUFFER_VIEW_TYPE_TO_VERTEX_ATTRIB_POINTER: Final[Mapping[Any, GlType]] = {
    ctypes.c_uint8: GL_UNSIGNED_BYTE,
    ctypes.c_uint16: GL_UNSIGNED_SHORT,
    ctypes.c_uint32: GL_UNSIGNED_INT,
}
