from __future__ import annotations

__all__ = [
    "MipmapSelection",
    "Texture",
    "TextureComponents",
    "TextureDataType",
    "TextureFilter",
    "TextureTarget",
    "TextureType",
    "TextureWrap",
]

# egraphics
from ._egraphics import GL_TEXTURE_2D
from ._egraphics import set_active_gl_texture_unit
from ._egraphics import set_gl_texture_target

# egraphics
from egraphics._weak_fifo_set import WeakFifoSet

# emath
from emath import FVector4
from emath import UVector2

# eplatform
from eplatform import Platform

# pyopengl
import OpenGL.GL
from OpenGL.GL import GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS
from OpenGL.GL import GL_TEXTURE_BORDER_COLOR
from OpenGL.GL import GL_TEXTURE_MAG_FILTER
from OpenGL.GL import GL_TEXTURE_MIN_FILTER
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGenerateMipmap
from OpenGL.GL import glGetIntegerv
from OpenGL.GL import glTexImage2D
from OpenGL.GL import glTexParameterf
from OpenGL.GL import glTexParameterfv
from OpenGL.GL import glTexParameteri
from OpenGL.GL.EXT.texture_filter_anisotropic import GL_TEXTURE_MAX_ANISOTROPY_EXT
from OpenGL.GL.EXT.texture_filter_anisotropic import glInitTextureFilterAnisotropicEXT
from OpenGL.error import GLError
from OpenGL.error import NullFunctionError

# python
from collections.abc import Buffer
import ctypes
from ctypes import sizeof as c_sizeof
from enum import Enum
from math import prod
from typing import Any
from typing import ClassVar
from typing import Final
from typing import Mapping
from typing import NamedTuple
from typing import Self
from weakref import ref

_DEFAULT_TEXTURE_UNIT: Final[int] = 0
_FIRST_BINDABLE_TEXTURE_UNIT: Final[int] = 1


class TextureTarget:
    _texture_unit: ClassVar[int] = -1
    _targets: ClassVar[list[TextureTarget]] = []

    TEXTURE_2D: ClassVar[Self]

    _bound: bool = False

    def __init__(self, gl_target: Any):
        self._targets.append(self)
        self._gl_target = gl_target
        self._unit_texture: dict[int, ref[Texture] | None] = {}

    def _set_texture(self, texture: Texture, unit: int, *, unit_only: bool = False) -> None:
        if not unit_only:
            if self._bound:
                raise RuntimeError("texture already bound to target")
            self._bound = True

        unit_texture_ref = self._unit_texture.get(unit)
        unit_texture: Texture | None
        if unit_texture_ref is None:
            unit_texture = unit_texture_ref
        else:
            unit_texture = unit_texture_ref()
        if unit_only and unit_texture is texture:
            return

        if self._texture_unit != unit:
            set_active_gl_texture_unit(unit)
            if (unit_only and not self._bound) or not unit_only:
                self.__class__._texture_unit = unit

        if unit_texture is texture:
            return

        set_gl_texture_target(self._gl_target, texture._gl)
        self._unit_texture[unit] = ref(texture)

        if self._bound and unit_only:
            set_active_gl_texture_unit(self.__class__._texture_unit)

    def _unset_texture(self) -> None:
        self._bound = False


TextureTarget.TEXTURE_2D = TextureTarget(GL_TEXTURE_2D)


@Platform.register_deactivate_callback
def _reset_texture_target_state() -> None:
    TextureTarget._texture_unit = -1
    for target in TextureTarget._targets:
        target._unit_texture = {}
        target._bound = False


class _TextureType(NamedTuple):
    size_length: int
    wrap_length: int
    target: TextureTarget


class TextureType(Enum):
    TWO_DIMENSIONS = _TextureType(2, 2, TextureTarget.TEXTURE_2D)


class TextureComponents(Enum):
    R = OpenGL.GL.GL_RED
    RG = OpenGL.GL.GL_RG
    RGB = OpenGL.GL.GL_RGB
    RGBA = OpenGL.GL.GL_RGBA


class TextureWrap(Enum):
    CLAMP_TO_EDGE = OpenGL.GL.GL_CLAMP_TO_EDGE
    CLAMP_TO_COLOR = OpenGL.GL.GL_CLAMP_TO_BORDER
    REPEAT = OpenGL.GL.GL_REPEAT
    REPEAT_MIRRORED = OpenGL.GL.GL_MIRRORED_REPEAT
    REPEAT_MIRRORED_THEN_CLAMP_TO_EDGE = OpenGL.GL.GL_MIRROR_CLAMP_TO_EDGE


class MipmapSelection(Enum):
    NONE = 0
    NEAREST = 1
    LINEAR = 2


class TextureFilter(Enum):
    NEAREST = 0
    LINEAR = 1


TextureDataType = (
    ctypes.c_uint8
    | ctypes.c_int8
    | ctypes.c_uint16
    | ctypes.c_int16
    | ctypes.c_uint32
    | ctypes.c_int32
    | ctypes.c_float
)

_GL_TEXTURE_WRAP_NAMES: Final = (
    OpenGL.GL.GL_TEXTURE_WRAP_S,
    OpenGL.GL.GL_TEXTURE_WRAP_T,
    OpenGL.GL.GL_TEXTURE_WRAP_R,
)

_TEXTURE_DATA_TYPE_TO_GL_DATA_TYPE: Final[Mapping[type[TextureDataType], Any]] = {
    ctypes.c_uint8: OpenGL.GL.GL_UNSIGNED_BYTE,
    ctypes.c_int8: OpenGL.GL.GL_BYTE,
    ctypes.c_uint16: OpenGL.GL.GL_UNSIGNED_SHORT,
    ctypes.c_int16: OpenGL.GL.GL_SHORT,
    ctypes.c_uint32: OpenGL.GL.GL_UNSIGNED_INT,
    ctypes.c_int32: OpenGL.GL.GL_INT,
    ctypes.c_float: OpenGL.GL.GL_FLOAT,
}

_TEXTURE_COMPONENTS_COUNT: Final[Mapping[TextureComponents, int]] = {
    TextureComponents.R: 1,
    TextureComponents.RG: 2,
    TextureComponents.RGB: 3,
    TextureComponents.RGBA: 4,
}


_TEXTURE_FILTER_TO_GL_MIN_FILTER: Final[Mapping[tuple[MipmapSelection, TextureFilter], Any]] = {
    (MipmapSelection.NONE, TextureFilter.NEAREST): OpenGL.GL.GL_NEAREST,
    (MipmapSelection.NONE, TextureFilter.LINEAR): OpenGL.GL.GL_LINEAR,
    (MipmapSelection.NEAREST, TextureFilter.NEAREST): OpenGL.GL.GL_NEAREST_MIPMAP_NEAREST,
    (MipmapSelection.NEAREST, TextureFilter.LINEAR): OpenGL.GL.GL_NEAREST_MIPMAP_LINEAR,
    (MipmapSelection.LINEAR, TextureFilter.NEAREST): OpenGL.GL.GL_LINEAR_MIPMAP_NEAREST,
    (MipmapSelection.LINEAR, TextureFilter.LINEAR): OpenGL.GL.GL_LINEAR_MIPMAP_LINEAR,
}


_TEXTURE_FILTER_TO_GL_MAG_FILTER: Final[Mapping[TextureFilter, Any]] = {
    TextureFilter.NEAREST: OpenGL.GL.GL_NEAREST,
    TextureFilter.LINEAR: OpenGL.GL.GL_LINEAR,
}


class Texture:
    _gl: Any = None

    _max_unit: ClassVar[int | None] = None
    _next_unit: ClassVar[int] = _FIRST_BINDABLE_TEXTURE_UNIT
    _unbound_units: ClassVar[WeakFifoSet[Texture]] = WeakFifoSet()
    _unit: int | None = None
    _open_units: set[int] = set()

    def __init__(
        self,
        type: TextureType,
        *,
        anisotropy: float | None = None,
        size: UVector2,
        components: TextureComponents,
        data_type: type[TextureDataType],
        buffer: Buffer,
        mipmap_selection: MipmapSelection | None = None,
        minify_filter: TextureFilter | None = None,
        magnify_filter: TextureFilter | None = None,
        wrap: tuple[TextureWrap, TextureWrap] | None = None,
        wrap_color: FVector4 | None = None,
    ):
        self._type = type
        # set defaults
        if mipmap_selection is None:
            mipmap_selection = MipmapSelection.NONE
        if minify_filter is None:
            minify_filter = TextureFilter.NEAREST
        if magnify_filter is None:
            magnify_filter = TextureFilter.NEAREST
        if wrap is None:
            wrap = tuple(  # type: ignore
                TextureWrap.REPEAT for _ in range(self._type.value.wrap_length)
            )
            assert wrap is not None
        if wrap_color is None:
            wrap_color = FVector4(0, 0, 0, 0)
        if anisotropy is None:
            anisotropy = 1.0
        # check the size
        for value, name in zip(size, ["width", "height"]):
            if value < 1:
                raise ValueError(f"{name} must be > 0")
        # check components and get the number of components for the given
        gl_data_type = _TEXTURE_DATA_TYPE_TO_GL_DATA_TYPE[data_type]
        component_count = _TEXTURE_COMPONENTS_COUNT[components]
        self._components = components
        # check filters
        gl_min_filter = _TEXTURE_FILTER_TO_GL_MIN_FILTER[(mipmap_selection, minify_filter)]
        gl_mag_filter = _TEXTURE_FILTER_TO_GL_MAG_FILTER[magnify_filter]
        # ensure the length of the data buffer is what we expect give the size,
        # component count and data type
        expected_data_length = prod(size) * component_count * c_sizeof(data_type)
        if memoryview(buffer).nbytes != expected_data_length:
            raise ValueError("too much or not enough data")
        # generate the texture and copy the data to it
        self._gl = glGenTextures(1)
        with self.bind():
            gl_target = self._type.value.target._gl_target
            assert type == TextureType.TWO_DIMENSIONS
            glTexImage2D(
                gl_target,
                0,
                components.value,
                size.x,
                size.y,
                0,
                components.value,
                gl_data_type,
                buffer,
            )
            self._size = size
            # we only need to generate mipmaps if we're using a mipmap selection
            # that would actually check the mipmaps
            self._mipmap_selection = mipmap_selection
            if mipmap_selection != MipmapSelection.NONE:
                glGenerateMipmap(gl_target)
            # set the min/max filter parameters
            self._minify_filter = minify_filter
            self._magnify_filter = magnify_filter
            glTexParameteri(gl_target, GL_TEXTURE_MIN_FILTER, gl_min_filter)
            glTexParameteri(gl_target, GL_TEXTURE_MAG_FILTER, gl_mag_filter)
            # set the wrapping parameters
            self._wrap = wrap
            self._wrap_color = wrap_color
            for wrap_value, wrap_name in zip(wrap, _GL_TEXTURE_WRAP_NAMES):
                glTexParameteri(gl_target, wrap_name, wrap_value.value)
            glTexParameterfv(gl_target, GL_TEXTURE_BORDER_COLOR, wrap_color.pointer)
            # set anisotropy
            self._anisotropy = anisotropy
            if anisotropy > 1.0 and glInitTextureFilterAnisotropicEXT():
                glTexParameterf(gl_target, GL_TEXTURE_MAX_ANISOTROPY_EXT, anisotropy)

    def __del__(self) -> None:
        if self._unit is not None:
            self._release_unit()
        if self._gl is not None:
            try:
                glDeleteTextures([self._gl])
            except (TypeError, NullFunctionError, GLError):
                pass
            self._gl = None

    def __repr__(self) -> str:
        cls = type(self)
        size_str = "x".join(str(c) for c in self._size)
        return f"<Texture {self.type.name!r} {size_str} {self.components.name!r}>"

    def _acquire_unit(self) -> None:
        if self._open_units:
            self._unit = self._open_units.pop()
            return
        assert self._next_unit <= self._get_max_unit()
        if self._next_unit == self._get_max_unit():
            self._steal_unit()
        else:
            self._unit = self._next_unit
            Texture._next_unit += 1

    def _release_unit(self) -> None:
        assert self._unit is not None
        self._open_units.add(self._unit)
        self._unit = None
        try:
            self._unbound_units.remove(self)
        except KeyError:
            pass

    def _steal_unit(self) -> None:
        try:
            texture = self._unbound_units.pop()
        except IndexError:
            raise RuntimeError("no texture unit available")
        texture._release_unit()
        self._acquire_unit()

    def _bind_unit(self) -> None:
        if self._unit is None:
            self._acquire_unit()
        assert self._unit is not None
        self._type.value.target._set_texture(self, self._unit, unit_only=True)

    def _unbind_unit(self) -> None:
        assert self._unit is not None
        self._unbound_units.add(self)

    def _bind(self) -> None:
        if self._unit is None:
            self._acquire_unit()
        assert self._unit is not None
        self._type.value.target._set_texture(self, self._unit)

    def _unbind(self) -> None:
        self._unbind_unit()
        self._type.value.target._unset_texture()

    @classmethod
    def _get_max_unit(cls) -> int:
        if cls._max_unit is None:
            cls._max_unit = glGetIntegerv(GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS)
        return cls._max_unit

    def bind_unit(self) -> _TextureUnitBind:
        return _TextureUnitBind(self)

    def bind(self) -> _TextureBind:
        return _TextureBind(self)

    @property
    def anisotropy(self) -> float:
        return self._anisotropy

    @property
    def components(self) -> TextureComponents:
        return self._components

    @property
    def magnify_filter(self) -> TextureFilter:
        return self._magnify_filter

    @property
    def minify_filter(self) -> TextureFilter:
        return self._minify_filter

    @property
    def mipmap_selection(self) -> MipmapSelection:
        return self._mipmap_selection

    @property
    def size(self) -> UVector2:
        return self._size

    @property
    def type(self) -> TextureType:
        return self._type

    @property
    def wrap(self) -> tuple[TextureWrap, TextureWrap]:
        return self._wrap

    @property
    def wrap_color(self) -> FVector4:
        return self._wrap_color


@Platform.register_deactivate_callback
def _reset_texture_state() -> None:
    Texture._max_unit = None
    Texture._next_unit = _FIRST_BINDABLE_TEXTURE_UNIT
    Texture._open_units.clear()
    Texture._unbound_units.clear()


class _TextureUnitBind:
    _refs: int = 0

    def __init__(self, texture: Texture):
        self._texture = texture

    def __enter__(self) -> int:
        if self._refs == 0:
            self._texture._bind_unit()
        self._refs += 1
        assert self._texture._unit is not None
        return self._texture._unit

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self._refs -= 1
        if self._refs == 0:
            self._texture._unbind_unit()
        assert self._refs >= 0


class _TextureBind:
    def __init__(self, texture: Texture):
        self._texture = texture

    def __enter__(self) -> None:
        self._texture._bind()

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self._texture._unbind()
