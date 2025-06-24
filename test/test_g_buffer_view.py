import ctypes
from struct import unpack as c_unpack

import emath
import pytest

from egraphics import GBuffer
from egraphics import GBufferView
from egraphics._g_buffer_view import _get_size_of_bvt

VIEW_DATA_TYPES = (
    ctypes.c_float,
    ctypes.c_double,
    ctypes.c_int8,
    ctypes.c_uint8,
    ctypes.c_int16,
    ctypes.c_uint16,
    ctypes.c_int32,
    ctypes.c_uint32,
    emath.FVector2,
    emath.DVector2,
    emath.I8Vector2,
    emath.I16Vector2,
    emath.I32Vector2,
    emath.U8Vector2,
    emath.U16Vector2,
    emath.U32Vector2,
    emath.FVector3,
    emath.DVector3,
    emath.I8Vector3,
    emath.I16Vector3,
    emath.I32Vector3,
    emath.U8Vector3,
    emath.U16Vector3,
    emath.U32Vector3,
    emath.FVector4,
    emath.DVector4,
    emath.I8Vector4,
    emath.I16Vector4,
    emath.I32Vector4,
    emath.U8Vector4,
    emath.U16Vector4,
    emath.U32Vector4,
    emath.FMatrix2x2,
    emath.DMatrix2x2,
    emath.FMatrix2x3,
    emath.DMatrix2x3,
    emath.FMatrix2x4,
    emath.DMatrix2x4,
    emath.FMatrix3x2,
    emath.DMatrix3x2,
    emath.FMatrix3x3,
    emath.DMatrix3x3,
    emath.FMatrix3x4,
    emath.DMatrix3x4,
    emath.FMatrix4x2,
    emath.DMatrix4x2,
    emath.FMatrix4x3,
    emath.DMatrix4x3,
    emath.FMatrix4x4,
    emath.DMatrix4x4,
)

CTYPES_TO_STRUCT_NAME = {
    ctypes.c_float: "f",
    ctypes.c_double: "d",
    ctypes.c_int8: "b",
    ctypes.c_uint8: "B",
    ctypes.c_int16: "h",
    ctypes.c_uint16: "H",
    ctypes.c_int32: "i",
    ctypes.c_uint32: "I",
}


@pytest.mark.parametrize("data_type", VIEW_DATA_TYPES)
def test_init_defaults(platform, data_type):
    buffer = GBuffer(0)
    view = GBufferView(buffer, data_type)
    assert view.g_buffer is buffer
    assert view.data_type is data_type
    assert view.stride == _get_size_of_bvt(data_type)
    assert view.length == len(buffer)
    assert view.offset == 0
    assert view.instancing_divisor is None
    assert len(view) == 0


@pytest.mark.parametrize(
    "array, data_type",
    [
        [emath.FVector2Array(emath.FVector2(-1), emath.FVector2(1)), emath.FVector2],
        [emath.DVector2Array(emath.DVector2(-1), emath.DVector2(1)), emath.DVector2],
        [emath.I8Vector2Array(emath.I8Vector2(-1), emath.I8Vector2(1)), emath.I8Vector2],
        [emath.U8Vector2Array(emath.U8Vector2(0), emath.U8Vector2(1)), emath.U8Vector2],
        [emath.I16Vector2Array(emath.I16Vector2(-1), emath.I16Vector2(1)), emath.I16Vector2],
        [emath.U16Vector2Array(emath.U16Vector2(0), emath.U16Vector2(1)), emath.U16Vector2],
        [emath.I32Vector2Array(emath.I32Vector2(-1), emath.I32Vector2(1)), emath.I32Vector2],
        [emath.U32Vector2Array(emath.U32Vector2(0), emath.U32Vector2(1)), emath.U32Vector2],
        [emath.FVector3Array(emath.FVector3(-1), emath.FVector3(1)), emath.FVector3],
        [emath.DVector3Array(emath.DVector3(-1), emath.DVector3(1)), emath.DVector3],
        [emath.I8Vector3Array(emath.I8Vector3(-1), emath.I8Vector3(1)), emath.I8Vector3],
        [emath.U8Vector3Array(emath.U8Vector3(0), emath.U8Vector3(1)), emath.U8Vector3],
        [emath.I16Vector3Array(emath.I16Vector3(-1), emath.I16Vector3(1)), emath.I16Vector3],
        [emath.U16Vector3Array(emath.U16Vector3(0), emath.U16Vector3(1)), emath.U16Vector3],
        [emath.I32Vector3Array(emath.I32Vector3(-1), emath.I32Vector3(1)), emath.I32Vector3],
        [emath.U32Vector3Array(emath.U32Vector3(0), emath.U32Vector3(1)), emath.U32Vector3],
        [emath.FVector4Array(emath.FVector4(-1), emath.FVector4(1)), emath.FVector4],
        [emath.DVector4Array(emath.DVector4(-1), emath.DVector4(1)), emath.DVector4],
        [emath.I8Vector4Array(emath.I8Vector4(-1), emath.I8Vector4(1)), emath.I8Vector4],
        [emath.U8Vector4Array(emath.U8Vector4(0), emath.U8Vector4(1)), emath.U8Vector4],
        [emath.I16Vector4Array(emath.I16Vector4(-1), emath.I16Vector4(1)), emath.I16Vector4],
        [emath.U16Vector4Array(emath.U16Vector4(0), emath.U16Vector4(1)), emath.U16Vector4],
        [emath.I32Vector4Array(emath.I32Vector4(-1), emath.I32Vector4(1)), emath.I32Vector4],
        [emath.U32Vector4Array(emath.U32Vector4(0), emath.U32Vector4(1)), emath.U32Vector4],
        [emath.FMatrix2x2Array(emath.FMatrix2x2(-1), emath.FMatrix2x2(1)), emath.FMatrix2x2],
        [emath.DMatrix2x2Array(emath.DMatrix2x2(-1), emath.DMatrix2x2(1)), emath.DMatrix2x2],
        [emath.FMatrix2x3Array(emath.FMatrix2x3(-1), emath.FMatrix2x3(1)), emath.FMatrix2x3],
        [emath.DMatrix2x3Array(emath.DMatrix2x3(-1), emath.DMatrix2x3(1)), emath.DMatrix2x3],
        [emath.FMatrix2x4Array(emath.FMatrix2x4(-1), emath.FMatrix2x4(1)), emath.FMatrix2x4],
        [emath.DMatrix2x4Array(emath.DMatrix2x4(-1), emath.DMatrix2x4(1)), emath.DMatrix2x4],
        [emath.FMatrix3x2Array(emath.FMatrix3x2(-1), emath.FMatrix3x2(1)), emath.FMatrix3x2],
        [emath.DMatrix3x2Array(emath.DMatrix3x2(-1), emath.DMatrix3x2(1)), emath.DMatrix3x2],
        [emath.FMatrix3x3Array(emath.FMatrix3x3(-1), emath.FMatrix3x3(1)), emath.FMatrix3x3],
        [emath.DMatrix3x3Array(emath.DMatrix3x3(-1), emath.DMatrix3x3(1)), emath.DMatrix3x3],
        [emath.FMatrix3x4Array(emath.FMatrix3x4(-1), emath.FMatrix3x4(1)), emath.FMatrix3x4],
        [emath.DMatrix3x4Array(emath.DMatrix3x4(-1), emath.DMatrix3x4(1)), emath.DMatrix3x4],
        [emath.FMatrix4x2Array(emath.FMatrix4x2(-1), emath.FMatrix4x2(1)), emath.FMatrix4x2],
        [emath.DMatrix4x2Array(emath.DMatrix4x2(-1), emath.DMatrix4x2(1)), emath.DMatrix4x2],
        [emath.FMatrix4x3Array(emath.FMatrix4x3(-1), emath.FMatrix4x3(1)), emath.FMatrix4x3],
        [emath.DMatrix4x3Array(emath.DMatrix4x3(-1), emath.DMatrix4x3(1)), emath.DMatrix4x3],
        [emath.FMatrix4x4Array(emath.FMatrix4x4(-1), emath.FMatrix4x4(1)), emath.FMatrix4x4],
        [emath.DMatrix4x4Array(emath.DMatrix4x4(-1), emath.DMatrix4x4(1)), emath.DMatrix4x4],
        [emath.FArray(-1, 1), ctypes.c_float],
        [emath.DArray(-1, 1), ctypes.c_double],
        [emath.I8Array(-1, 1), ctypes.c_int8],
        [emath.U8Array(0, 1), ctypes.c_uint8],
        [emath.I16Array(-1, 1), ctypes.c_int16],
        [emath.U16Array(0, 1), ctypes.c_uint16],
        [emath.I32Array(-1, 1), ctypes.c_int32],
        [emath.U32Array(0, 1), ctypes.c_uint32],
    ],
)
@pytest.mark.parametrize("instancing_divisor", [None, 1])
def test_from_array(platform, array, data_type, instancing_divisor):
    view = GBufferView.from_array(array, instancing_divisor=instancing_divisor)
    assert bytes(view.g_buffer) == bytes(array)
    assert view.data_type is data_type
    assert view.stride == _get_size_of_bvt(data_type)
    assert view.length == len(view.g_buffer)
    assert view.offset == 0
    assert view.instancing_divisor == instancing_divisor
    assert list(view) == list(array)


@pytest.mark.parametrize("data_type", VIEW_DATA_TYPES)
def test_empty_buffer(platform, data_type) -> None:
    view = GBufferView(GBuffer(), data_type)
    assert len(view) == 0
    assert list(view) == []


@pytest.mark.parametrize("stride", [-100, -1, 0])
def test_non_positive_stride(platform, stride) -> None:
    with pytest.raises(ValueError) as excinfo:
        GBufferView(GBuffer(), ctypes.c_float, stride=stride)
    assert str(excinfo.value) == "stride must be greater than 0"


@pytest.mark.parametrize("offset", [-100, -1])
def test_negative_offset(platform, offset) -> None:
    with pytest.raises(ValueError) as excinfo:
        GBufferView(GBuffer(), ctypes.c_float, offset=offset)
    assert str(excinfo.value) == "offset must be 0 or greater"


@pytest.mark.parametrize("length", [-100, -1])
def test_negative_length(platform, length) -> None:
    with pytest.raises(ValueError) as excinfo:
        GBufferView(GBuffer(), ctypes.c_float, length=length)
    assert str(excinfo.value) == "length must be 0 or greater"


@pytest.mark.parametrize("length, offset", [(0, 1), (1, 0)])
def test_length_offset_overflow(platform, length, offset) -> None:
    with pytest.raises(ValueError) as excinfo:
        GBufferView(GBuffer(), ctypes.c_float, length=length, offset=offset)
    assert str(excinfo.value) == "length/offset goes beyond buffer size"


@pytest.mark.parametrize("instancing_divisor", [-100, -1, 0])
def test_non_positive_instancing_divisor(platform, instancing_divisor) -> None:
    with pytest.raises(ValueError) as excinfo:
        GBufferView(GBuffer(), ctypes.c_float, instancing_divisor=instancing_divisor)
    assert str(excinfo.value) == "instancing divisor must be greater than 0"


@pytest.mark.parametrize("data_type", VIEW_DATA_TYPES)
@pytest.mark.parametrize("add_stride", [0, 1, 2, 4])
@pytest.mark.parametrize("item_length", [None, 4])
@pytest.mark.parametrize("offset", [0, 1, 2, 4])
@pytest.mark.parametrize("instancing_divisor", [None, 1, 2])
def test_read(platform, data_type, add_stride, item_length, offset, instancing_divisor):
    data = bytes(range(255)) * 10
    stride = _get_size_of_bvt(data_type) + add_stride
    if item_length is None:
        length = None
        expected_length = (len(data) - offset + add_stride) // stride
    else:
        length = item_length
        expected_length = (length + add_stride) // stride
    expected_python_data = []
    for i in range(expected_length):
        data_start = offset + (stride * i)
        data_bytes = data[data_start : data_start + _get_size_of_bvt(data_type)]
        try:
            struct_name = CTYPES_TO_STRUCT_NAME[data_type]
            expected_python_data.append(c_unpack(struct_name, data_bytes)[0])
        except KeyError:
            expected_python_data.append(data_type.from_buffer(data_bytes))

    view = GBufferView(
        GBuffer(data),
        data_type,
        length=length,
        stride=stride,
        offset=offset,
        instancing_divisor=instancing_divisor,
    )
    assert len(view) == expected_length
    assert list(view) == expected_python_data
