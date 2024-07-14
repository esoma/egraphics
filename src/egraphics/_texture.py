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
from ._egraphics import GL_BYTE
from ._egraphics import GL_CLAMP_TO_BORDER
from ._egraphics import GL_CLAMP_TO_EDGE
from ._egraphics import GL_FLOAT
from ._egraphics import GL_INT
from ._egraphics import GL_LINEAR
from ._egraphics import GL_LINEAR_MIPMAP_LINEAR
from ._egraphics import GL_LINEAR_MIPMAP_NEAREST
from ._egraphics import GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_VALUE
from ._egraphics import GL_MIRRORED_REPEAT
from ._egraphics import GL_NEAREST
from ._egraphics import GL_NEAREST_MIPMAP_LINEAR
from ._egraphics import GL_NEAREST_MIPMAP_NEAREST
from ._egraphics import GL_RED
from ._egraphics import GL_REPEAT
from ._egraphics import GL_RG
from ._egraphics import GL_RGB
from ._egraphics import GL_RGBA
from ._egraphics import GL_SHORT
from ._egraphics import GL_TEXTURE_2D
from ._egraphics import GL_UNSIGNED_BYTE
from ._egraphics import GL_UNSIGNED_INT
from ._egraphics import GL_UNSIGNED_SHORT
from ._egraphics import GlTexture
from ._egraphics import GlTextureFilter
from ._egraphics import GlTextureWrap
from ._egraphics import GlType
from ._egraphics import create_gl_texture
from ._egraphics import delete_gl_texture
from ._egraphics import generate_gl_texture_target_mipmaps
from ._egraphics import set_active_gl_texture_unit
from ._egraphics import set_gl_texture_target
from ._egraphics import set_gl_texture_target_2d_data
from ._egraphics import set_gl_texture_target_parameters

# egraphics
from egraphics._weak_fifo_set import WeakFifoSet

# emath
from emath import FVector4
from emath import UVector2

# eplatform
from eplatform import Platform

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

        set_gl_texture_target(self._gl_target, texture._gl_texture)
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
    R = GL_RED
    RG = GL_RG
    RGB = GL_RGB
    RGBA = GL_RGBA


class TextureWrap(Enum):
    CLAMP_TO_EDGE = GL_CLAMP_TO_EDGE
    CLAMP_TO_COLOR = GL_CLAMP_TO_BORDER
    REPEAT = GL_REPEAT
    REPEAT_MIRRORED = GL_MIRRORED_REPEAT


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

_TEXTURE_DATA_TYPE_TO_GL_DATA_TYPE: Final[Mapping[type[TextureDataType], GlType]] = {
    ctypes.c_uint8: GL_UNSIGNED_BYTE,
    ctypes.c_int8: GL_BYTE,
    ctypes.c_uint16: GL_UNSIGNED_SHORT,
    ctypes.c_int16: GL_SHORT,
    ctypes.c_uint32: GL_UNSIGNED_INT,
    ctypes.c_int32: GL_INT,
    ctypes.c_float: GL_FLOAT,
}

_TEXTURE_COMPONENTS_COUNT: Final[Mapping[TextureComponents, int]] = {
    TextureComponents.R: 1,
    TextureComponents.RG: 2,
    TextureComponents.RGB: 3,
    TextureComponents.RGBA: 4,
}


_TEXTURE_FILTER_TO_GL_MIN_FILTER: Final[
    Mapping[tuple[MipmapSelection, TextureFilter], GlTextureFilter]
] = {
    (MipmapSelection.NONE, TextureFilter.NEAREST): GL_NEAREST,
    (MipmapSelection.NONE, TextureFilter.LINEAR): GL_LINEAR,
    (MipmapSelection.NEAREST, TextureFilter.NEAREST): GL_NEAREST_MIPMAP_NEAREST,
    (MipmapSelection.NEAREST, TextureFilter.LINEAR): GL_NEAREST_MIPMAP_LINEAR,
    (MipmapSelection.LINEAR, TextureFilter.NEAREST): GL_LINEAR_MIPMAP_NEAREST,
    (MipmapSelection.LINEAR, TextureFilter.LINEAR): GL_LINEAR_MIPMAP_LINEAR,
}


_TEXTURE_FILTER_TO_GL_MAG_FILTER: Final[Mapping[TextureFilter, GlTextureFilter]] = {
    TextureFilter.NEAREST: GL_NEAREST,
    TextureFilter.LINEAR: GL_LINEAR,
}


class Texture:
    _gl_texture: GlTexture | None = None

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
        self._gl_texture = create_gl_texture()
        with self.bind():
            gl_target = self._type.value.target._gl_target
            assert type == TextureType.TWO_DIMENSIONS
            set_gl_texture_target_2d_data(gl_target, components.value, size, gl_data_type, buffer)
            self._size = size
            # we only need to generate mipmaps if we're using a mipmap selection
            # that would actually check the mipmaps
            self._mipmap_selection = mipmap_selection
            if mipmap_selection != MipmapSelection.NONE:
                generate_gl_texture_target_mipmaps(gl_target)
            # set parameters
            self._minify_filter = minify_filter
            self._magnify_filter = magnify_filter
            self._wrap = wrap
            self._wrap_color = wrap_color
            self._anisotropy = anisotropy

            gl_wrap_args: tuple[GlTextureWrap, GlTextureWrap | None, GlTextureWrap | None] = tuple(
                (
                    *(w.value for w in wrap),
                    *(None for i in range(3 - len(wrap))),
                )
            )  # type: ignore
            set_gl_texture_target_parameters(
                gl_target, gl_min_filter, gl_mag_filter, *gl_wrap_args, wrap_color, anisotropy
            )

    def __del__(self) -> None:
        if self._unit is not None:
            self._release_unit()
        if self._gl_texture is not None:
            delete_gl_texture(self._gl_texture)
            self._gl_texture = None

    def __repr__(self) -> str:
        cls = type(self)
        size_str = "x".join(str(c) for c in self._size)
        return f"<Texture {self.type.name!r} {size_str} {self.components.name!r}>"

    def _acquire_unit(self) -> None:
        if self._open_units:
            self._unit = self._open_units.pop()
            return
        assert self._next_unit <= GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_VALUE
        if self._next_unit == GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_VALUE:
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
