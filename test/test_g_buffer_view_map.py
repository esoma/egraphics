# egraphics
from egraphics import GBuffer
from egraphics import GBufferView
from egraphics import GBufferViewMap

# pytest
import pytest

# python
import ctypes


@pytest.mark.parametrize("indices", [(0, 10), None])
def test_read_only(platform, indices) -> None:
    if indices is None:
        indices = GBufferView(GBuffer(), ctypes.c_uint8)

    bv_1 = GBufferView(GBuffer(), ctypes.c_float)
    bv_2 = GBufferView(GBuffer(), ctypes.c_float)
    map = {
        "vbo_1": bv_1,
        "vbo_2": bv_2,
    }
    bvm = GBufferViewMap(map, indices)

    assert len(bvm) == 2
    assert bvm["vbo_1"] is bv_1
    assert bvm["vbo_2"] is bv_2
    assert indices == indices

    with pytest.raises(KeyError):
        bvm["vbo_3"]

    with pytest.raises(TypeError):
        bvm["vbo_1"] = GBufferView(GBuffer(), ctypes.c_float)  # type: ignore

    with pytest.raises(AttributeError):
        bvm.indices = None

    map.clear()
    assert len(bvm) == 2
    assert bvm["vbo_1"] is bv_1
    assert bvm["vbo_2"] is bv_2


def test_index_buffer_view_invalid_type(platform):
    index_buffer_view = GBufferView(GBuffer(), ctypes.c_int32)
    with pytest.raises(ValueError) as excinfo:
        GBufferViewMap({}, index_buffer_view)
    assert str(excinfo.value) == (
        f"view buffer with type {ctypes.c_int32} cannot be used for indexing"
    )


def test_index_buffer_view_different_stride(platform):
    index_buffer_view = GBufferView(GBuffer(), ctypes.c_int32, stride=1)
    with pytest.raises(ValueError) as excinfo:
        GBufferViewMap({}, index_buffer_view)
    assert str(excinfo.value) == (
        f"view buffer with a stride different from its type cannot be used " f"for indexing"
    )


def test_index_buffer_view_different_offset(platform):
    index_buffer_view = GBufferView(GBuffer(), ctypes.c_int32, offset=1)
    with pytest.raises(ValueError) as excinfo:
        GBufferViewMap({}, index_buffer_view)
    assert str(excinfo.value) == (
        f"view buffer with an offset other than 0 cannot be used for indexing"
    )


def test_index_buffer_view_with_instancing_divisor(platform):
    index_buffer_view = GBufferView(GBuffer(), ctypes.c_int32, instancing_divisor=1)
    with pytest.raises(ValueError) as excinfo:
        GBufferViewMap({}, index_buffer_view)
    assert str(excinfo.value) == (
        f"view buffer with instancing_divisor cannot be used for indexing"
    )
