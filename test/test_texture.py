from __future__ import annotations

__all__ = ["TextureTest"]


import ctypes
from ctypes import sizeof as c_sizeof
from math import prod
from unittest.mock import patch

import pytest
from emath import FVector4
from emath import UVector2
from OpenGL.GL import GL_ACTIVE_TEXTURE
from OpenGL.GL import GL_IMAGE_BINDING_NAME
from OpenGL.GL import GL_TEXTURE0
from OpenGL.GL import GL_TEXTURE_BINDING_2D
from OpenGL.GL import glActiveTexture
from OpenGL.GL import glGetIntegeri_v
from OpenGL.GL import glGetIntegerv
from OpenGL.GL import glIsTexture

from egraphics import MipmapSelection
from egraphics import Texture
from egraphics import TextureComponents
from egraphics import TextureFilter
from egraphics import TextureType
from egraphics import TextureWrap
from egraphics._texture import _FIRST_BINDABLE_TEXTURE_UNIT
from egraphics._texture import _TextureTarget
from egraphics._texture import bind_texture
from egraphics._texture import bind_texture_image_unit
from egraphics._texture import bind_texture_unit

TEXTURE_COMPONENTS_COUNT = {
    TextureComponents.R: 1,
    TextureComponents.RG: 2,
    TextureComponents.RGB: 3,
    TextureComponents.RGBA: 4,
    TextureComponents.D: 1,
    TextureComponents.X: 1,
    TextureComponents.XY: 2,
    TextureComponents.XYZ: 3,
    TextureComponents.XYZW: 4,
}


TEXTURE_DATA_TYPE_MAX = {
    ctypes.c_uint8: 255,
    ctypes.c_int8: 127,
    ctypes.c_uint16: 65535,
    ctypes.c_int16: 32767,
    ctypes.c_uint32: 4294967295,
    ctypes.c_int32: 2147483647,
    ctypes.c_float: 1.0,
}


TEXTURE_DATA_TYPE_STRUCT = {
    ctypes.c_uint8: "B",
    ctypes.c_int8: "b",
    ctypes.c_uint16: "H",
    ctypes.c_int16: "h",
    ctypes.c_uint32: "I",
    ctypes.c_int32: "i",
    ctypes.c_float: "f",
}


TEXTURE_DATA_TYPES: Final = tuple(TEXTURE_DATA_TYPE_MAX)


class TextureTest:
    size_length: int
    wrap_length: int
    data_multiplier = 1

    @classmethod
    def create_texture(
        cls,
        size,
        components,
        data_type,
        data,
        *,
        anisotropy=None,
        mipmap_selection=None,
        minify_filter=None,
        magnify_filter=None,
        wrap=None,
        wrap_color=None,
    ) -> Texture:
        raise NotImplementedError()

    @pytest.fixture
    def size_type(self):
        return {2: UVector2}[self.size_length]

    @pytest.fixture
    def size(self, size_type):
        return size_type(*(1 for _ in range(self.size_length)))

    def test_no_data(self, platform, size):
        self.create_texture(size, TextureComponents.R, ctypes.c_int8, None)

    def test_repr(self, platform, size):
        texture = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        repr(texture)

    @pytest.mark.parametrize("width", [0])
    def test_width_out_of_range(self, platform, width, size, size_type):
        size = list(size)
        size[0] = width
        size = size_type(*size)
        with pytest.raises(ValueError) as excinfo:
            self.create_texture(size, TextureComponents.R, ctypes.c_int8, b"")
        assert str(excinfo.value) == "width must be > 0"

    @pytest.mark.parametrize("height", [0])
    def test_height_out_of_range(self, platform, height, size, size_type):
        if self.size_length < 2:
            pytest.skip("texture has no height")
        size = list(size)
        size[1] = height
        size = size_type(*size)
        with pytest.raises(ValueError) as excinfo:
            self.create_texture(size, TextureComponents.R, ctypes.c_int8, b"")
        assert str(excinfo.value) == "height must be > 0"

    def test_not_enough_data(self, platform, size):
        expected_data_length = prod(size)
        data = b"\x00" * (expected_data_length - 1) * self.data_multiplier
        with pytest.raises(ValueError) as excinfo:
            self.create_texture(size, TextureComponents.R, ctypes.c_int8, memoryview(data))
        assert str(excinfo.value) == "too much or not enough data"

    def test_too_much_data(self, platform, size):
        expected_data_length = prod(size)
        data = b"\x00" * (expected_data_length + 1) * self.data_multiplier
        with pytest.raises(ValueError) as excinfo:
            self.create_texture(size, TextureComponents.R, ctypes.c_int8, memoryview(data))
        assert str(excinfo.value) == "too much or not enough data"

    @pytest.mark.parametrize("components", TextureComponents)
    @pytest.mark.parametrize("data_type", TEXTURE_DATA_TYPES)
    def test_components_data_type_combinations(self, platform, size, components, data_type):
        data = (
            b"\x00"
            * TEXTURE_COMPONENTS_COUNT[components]
            * c_sizeof(data_type)
            * self.data_multiplier
        )
        texture = self.create_texture(size, components, data_type, memoryview(data))
        assert texture.components == components
        assert texture.size == size

    @pytest.mark.parametrize("mipmap_selection", MipmapSelection)
    @pytest.mark.parametrize("minify_filter", TextureFilter)
    @pytest.mark.parametrize("magnify_filter", TextureFilter)
    def test_min_mag_mip(self, platform, size, mipmap_selection, minify_filter, magnify_filter):
        data = b"\x00" * self.data_multiplier
        texture = self.create_texture(
            size,
            TextureComponents.R,
            ctypes.c_uint8,
            memoryview(data),
            mipmap_selection=mipmap_selection,
            minify_filter=minify_filter,
            magnify_filter=magnify_filter,
        )
        assert texture.components == TextureComponents.R
        assert texture.size == size
        assert texture.minify_filter == minify_filter
        assert texture.magnify_filter == magnify_filter
        assert texture.mipmap_selection == mipmap_selection

    @pytest.mark.parametrize("wrap_s", TextureWrap)
    @pytest.mark.parametrize("wrap_t", TextureWrap)
    @pytest.mark.parametrize("wrap_r", TextureWrap)
    def test_wrap(self, platform, size, wrap_s, wrap_t, wrap_r):
        data = b"\x00" * self.data_multiplier
        wrap: Any = (wrap_s, wrap_t, wrap_r)[: self.wrap_length]
        texture = self.create_texture(
            size, TextureComponents.R, ctypes.c_uint8, memoryview(data), wrap=wrap
        )
        assert texture.components == TextureComponents.R
        assert texture.size == size
        assert texture.wrap == wrap

    @pytest.mark.parametrize("wrap_color", [FVector4(0), FVector4(0.1, 0.2, 0.3, 0.4)])
    def test_wrap_color(self, platform, size, wrap_color):
        data = b"\x00" * self.data_multiplier
        texture = self.create_texture(
            size, TextureComponents.R, ctypes.c_uint8, memoryview(data), wrap_color=wrap_color
        )
        assert texture.components == TextureComponents.R
        assert texture.size == size
        assert texture.wrap_color == wrap_color

    @pytest.mark.parametrize("anisotropy", [-1000, 0, 1.0, 1.5, 16, 999999])
    def test_anisotropy_values(self, platform, size, anisotropy):
        data = b"\x00" * self.data_multiplier
        texture = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(data), anisotropy=anisotropy
        )
        assert texture.anisotropy == float(anisotropy)

    def test_delete(self, platform, size):
        texture = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )

        gl_texture = texture._gl_texture
        del texture
        assert not glIsTexture(gl_texture)

    def test_bind_texture_unit_gl_state(self, platform, size):
        texture_1 = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        texture_2 = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        with bind_texture_unit(texture_1) as unit_1:
            active_texture = glGetIntegerv(GL_ACTIVE_TEXTURE)
            assert active_texture != GL_TEXTURE0 + unit_1
            glActiveTexture(GL_TEXTURE0 + unit_1)
            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture
            glActiveTexture(active_texture)

            with bind_texture_unit(texture_2) as unit_2:
                assert glGetIntegerv(GL_ACTIVE_TEXTURE) == GL_TEXTURE0 + unit_2
                assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_2._gl_texture
                glActiveTexture(GL_TEXTURE0 + unit_1)
                assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture
                glActiveTexture(GL_TEXTURE0 + unit_2)

                with bind_texture_unit(texture_1) as unit_1_2:
                    assert unit_1 == unit_1_2
                    assert glGetIntegerv(GL_ACTIVE_TEXTURE) == GL_TEXTURE0 + unit_2
                    assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_2._gl_texture
                    glActiveTexture(GL_TEXTURE0 + unit_1)
                    assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture
                    glActiveTexture(GL_TEXTURE0 + unit_2)

                assert glGetIntegerv(GL_ACTIVE_TEXTURE) == GL_TEXTURE0 + unit_2
                assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_2._gl_texture
                glActiveTexture(GL_TEXTURE0 + unit_1)
                assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture
                glActiveTexture(GL_TEXTURE0 + unit_2)

            assert glGetIntegerv(GL_ACTIVE_TEXTURE) == GL_TEXTURE0 + unit_2
            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_2._gl_texture
            glActiveTexture(GL_TEXTURE0 + unit_1)
            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture
            glActiveTexture(GL_TEXTURE0 + unit_2)

        assert glGetIntegerv(GL_ACTIVE_TEXTURE) == GL_TEXTURE0 + unit_2
        assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_2._gl_texture
        glActiveTexture(GL_TEXTURE0 + unit_1)
        assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture
        glActiveTexture(GL_TEXTURE0 + unit_2)

        del texture_1
        del texture_2

        assert glGetIntegerv(GL_ACTIVE_TEXTURE) == GL_TEXTURE0 + unit_2
        assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == 0
        glActiveTexture(GL_TEXTURE0 + unit_1)
        assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == 0
        glActiveTexture(GL_TEXTURE0 + unit_2)

    def test_bind_texture_unit_gl_texture_lifetime(self, platform, size):
        texture = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        with bind_texture_unit(texture) as unit:
            gl_texture = texture._gl_texture
            del texture
            glActiveTexture(GL_TEXTURE0 + unit)
            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == gl_texture

    def test_bind_state(self, platform, size):
        texture_1 = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        texture_2 = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        with bind_texture(texture_1):
            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture

            with pytest.raises(RuntimeError) as excinfo:
                with bind_texture(texture_2):
                    pass
            assert str(excinfo.value) == "texture already bound to target"
            del excinfo

            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture

        assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture

        with bind_texture(texture_2):
            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_2._gl_texture

        del texture_1
        assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_2._gl_texture

        del texture_2
        assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == 0

    def test_bind_gl_texture_lifetime(self, platform, size):
        texture = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        with bind_texture(texture):
            gl_texture = texture._gl_texture
            del texture
            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == gl_texture

    def test_bind_and_bind_texture_unit_interaction(self, platform, size):
        texture_1 = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        texture_2 = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        texture_3 = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        del _TextureTarget.TEXTURE_2D._unit_texture[texture_3._texture_unit]

        with bind_texture_unit(texture_1) as unit_1:
            pass
        with bind_texture_unit(texture_2) as unit_2:
            pass

        with bind_texture(texture_1):
            assert glGetIntegerv(GL_ACTIVE_TEXTURE) == GL_TEXTURE0 + unit_1
            assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture

            with bind_texture_unit(texture_3) as unit_3:
                assert glGetIntegerv(GL_ACTIVE_TEXTURE) == GL_TEXTURE0 + unit_1
                assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_1._gl_texture

                glActiveTexture(GL_TEXTURE0 + unit_3)
                assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture_3._gl_texture

                glActiveTexture(GL_TEXTURE0 + unit_1)

    def test_steal_texture_unit(self, platform, size):
        with patch(
            "egraphics._texture.GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_VALUE",
            _FIRST_BINDABLE_TEXTURE_UNIT + 2,
        ):
            texture_1 = self.create_texture(
                size,
                TextureComponents.R,
                ctypes.c_int8,
                memoryview(b"\x00" * self.data_multiplier),
            )
            assert texture_1._texture_unit is not None
            unit_1 = texture_1._texture_unit

            texture_2 = self.create_texture(
                size,
                TextureComponents.R,
                ctypes.c_int8,
                memoryview(b"\x00" * self.data_multiplier),
            )
            assert texture_1._texture_unit == unit_1
            assert texture_2._texture_unit is not None
            unit_2 = texture_2._texture_unit

            texture_3 = self.create_texture(
                size,
                TextureComponents.R,
                ctypes.c_int8,
                memoryview(b"\x00" * self.data_multiplier),
            )
            assert texture_1._texture_unit is None
            assert texture_2._texture_unit == unit_2
            assert texture_3._texture_unit == unit_1

            with bind_texture_unit(texture_2):
                assert texture_1._texture_unit is None
                assert texture_2._texture_unit == unit_2
                assert texture_3._texture_unit == unit_1

            with bind_texture_unit(texture_1):
                assert texture_1._texture_unit == unit_1
                assert texture_2._texture_unit == unit_2
                assert texture_3._texture_unit is None

    def test_out_of_texture_units(self, platform, size):
        with patch(
            "egraphics._texture.GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_VALUE",
            _FIRST_BINDABLE_TEXTURE_UNIT + 1,
        ):
            texture_1 = self.create_texture(
                size,
                TextureComponents.R,
                ctypes.c_int8,
                memoryview(b"\x00" * self.data_multiplier),
            )
            texture_2 = self.create_texture(
                size,
                TextureComponents.R,
                ctypes.c_int8,
                memoryview(b"\x00" * self.data_multiplier),
            )
            with bind_texture_unit(texture_1):
                with pytest.raises(RuntimeError) as excinfo:
                    with bind_texture_unit(texture_2):
                        pass
                assert str(excinfo.value) == "no texture unit available"
                del excinfo

    def test_bind_texture_image_unit_gl_state(self, platform, size):
        texture_1 = self.create_texture(
            size, TextureComponents.XYZW, ctypes.c_float, memoryview(b"\x00" * 4 * 4)
        )
        texture_2 = self.create_texture(
            size, TextureComponents.XYZW, ctypes.c_float, memoryview(b"\x00" * 4 * 4)
        )
        with bind_texture_image_unit(texture_1) as unit_1:
            binding_1 = ctypes.c_int()
            glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_1, ctypes.byref(binding_1))
            assert binding_1.value == texture_1._gl_texture

            with bind_texture_image_unit(texture_2) as unit_2:
                binding_2 = ctypes.c_int()
                glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_2, ctypes.byref(binding_2))
                assert binding_2.value == texture_2._gl_texture
                glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_1, ctypes.byref(binding_1))
                assert binding_1.value == texture_1._gl_texture

                with bind_texture_image_unit(texture_1) as unit_1_2:
                    assert unit_1 == unit_1_2
                    glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_2, ctypes.byref(binding_2))
                    assert binding_2.value == texture_2._gl_texture
                    glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_1, ctypes.byref(binding_1))
                    assert binding_1.value == texture_1._gl_texture

                glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_2, ctypes.byref(binding_2))
                assert binding_2.value == texture_2._gl_texture
                glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_1, ctypes.byref(binding_1))
                assert binding_1.value == texture_1._gl_texture

            glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_2, ctypes.byref(binding_2))
            assert binding_2.value == texture_2._gl_texture
            glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_1, ctypes.byref(binding_1))
            assert binding_1.value == texture_1._gl_texture

        glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_2, ctypes.byref(binding_2))
        assert binding_2.value == texture_2._gl_texture
        glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_1, ctypes.byref(binding_1))
        assert binding_1.value == texture_1._gl_texture

        del texture_1
        del texture_2

        glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_2, ctypes.byref(binding_2))
        assert binding_2.value == 0
        glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit_1, ctypes.byref(binding_1))
        assert binding_1.value == 0

    def test_bind_texture_image_unit_gl_texture_lifetime(self, platform, size):
        texture = self.create_texture(
            size, TextureComponents.XYZW, ctypes.c_float, memoryview(b"\x00" * 4 * 4)
        )
        with bind_texture_image_unit(texture) as unit:
            gl_texture = texture._gl_texture
            del texture
            binding = ctypes.c_int()
            glGetIntegeri_v(GL_IMAGE_BINDING_NAME, unit, ctypes.byref(binding))
            assert binding.value == gl_texture

    def test_steal_texture_image_unit(self, platform, size):
        with patch("egraphics._texture.GL_MAX_IMAGE_UNITS_VALUE", 2):
            texture_1 = self.create_texture(
                size, TextureComponents.XYZW, ctypes.c_float, memoryview(b"\x00" * 4 * 4)
            )
            with bind_texture_image_unit(texture_1) as unit_1:
                pass
            assert texture_1._image_unit == unit_1

            texture_2 = self.create_texture(
                size, TextureComponents.XYZW, ctypes.c_float, memoryview(b"\x00" * 4 * 4)
            )
            with bind_texture_image_unit(texture_2) as unit_2:
                pass
            assert texture_1._image_unit == unit_1
            assert texture_2._image_unit == unit_2

            texture_3 = self.create_texture(
                size, TextureComponents.XYZW, ctypes.c_float, memoryview(b"\x00" * 4 * 4)
            )
            with bind_texture_image_unit(texture_3) as unit_3:
                pass
            assert texture_1._image_unit is None
            assert texture_2._image_unit == unit_2
            assert texture_3._image_unit == unit_3
            assert unit_1 == unit_3

            with bind_texture_image_unit(texture_2):
                assert texture_1._image_unit is None
                assert texture_2._image_unit == unit_2
                assert texture_3._image_unit == unit_3

            with bind_texture_image_unit(texture_1):
                assert texture_1._image_unit == unit_1
                assert texture_2._image_unit == unit_2
                assert texture_3._image_unit is None

    def test_out_of_texture_image_units(self, platform, size):
        with patch("egraphics._texture.GL_MAX_IMAGE_UNITS_VALUE", 1):
            texture_1 = self.create_texture(
                size, TextureComponents.XYZW, ctypes.c_float, memoryview(b"\x00" * 4 * 4)
            )
            texture_2 = self.create_texture(
                size, TextureComponents.XYZW, ctypes.c_float, memoryview(b"\x00" * 4 * 4)
            )
            with bind_texture_image_unit(texture_1):
                with pytest.raises(RuntimeError) as excinfo:
                    with bind_texture_image_unit(texture_2):
                        pass
                assert str(excinfo.value) == "no image unit available"
                del excinfo


class TextureTestType(TextureTest):
    texture_type: TextureType

    @classmethod
    def create_texture(
        cls,
        size,
        components,
        data_type,
        buffer,
        *,
        anisotropy=None,
        mipmap_selection=None,
        minify_filter=None,
        magnify_filter=None,
        wrap=None,
        wrap_color=None,
    ) -> Texture:
        return Texture(
            cls.texture_type,
            size=size,
            components=components,
            data_type=data_type,
            buffer=buffer,
            anisotropy=anisotropy,
            mipmap_selection=mipmap_selection,
            minify_filter=minify_filter,
            magnify_filter=magnify_filter,
            wrap=wrap,
            wrap_color=wrap_color,
        )

    def test_type(self, platform, size):
        texture = self.create_texture(
            size, TextureComponents.R, ctypes.c_int8, memoryview(b"\x00" * self.data_multiplier)
        )
        assert texture.type == self.texture_type


class TestTexture2d(TextureTestType):
    texture_type = TextureType.TWO_DIMENSIONS
    size_length = 2
    wrap_length = 2
