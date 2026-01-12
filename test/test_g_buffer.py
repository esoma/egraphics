import gc

import pytest

from egraphics import GBuffer
from egraphics import IndexGBuffer
from egraphics import ReadWriteGBuffer
from egraphics import VertexGBuffer
from egraphics import WriteGBuffer

BASIC_USABLE_BUFFER_CLS = (IndexGBuffer, VertexGBuffer)
WRITE_USABLE_BUFFER_CLS = tuple(
    type(f"Write{c.__name__}", (c, WriteGBuffer), {}) for c in BASIC_USABLE_BUFFER_CLS
)
READ_WRITE_USABLE_BUFFER_CLS = tuple(
    type(f"ReadWrite{c.__name__}", (c, ReadWriteGBuffer), {}) for c in BASIC_USABLE_BUFFER_CLS
)
USABLE_BUFFER_CLS = (
    *BASIC_USABLE_BUFFER_CLS,
    *WRITE_USABLE_BUFFER_CLS,
    *READ_WRITE_USABLE_BUFFER_CLS,
)


@pytest.mark.parametrize("cls", [GBuffer, WriteGBuffer, ReadWriteGBuffer])
def test_cannot_initialize(vulkan, cls):
    with pytest.raises(RuntimeError) as excinfo:
        cls(1)
    assert str(excinfo.value) == f"{cls.__name__} cannot be instantiated"


@pytest.mark.parametrize("cls", [IndexGBuffer, VertexGBuffer])
def test_initialize_no_vulkan_instance(cls):
    with pytest.raises(RuntimeError) as excinfo:
        cls(1)
    assert str(excinfo.value) == f"no vulkan context"


@pytest.mark.parametrize("cls", USABLE_BUFFER_CLS)
@pytest.mark.parametrize("length", [-1, 0])
def test_length_initialize_invalid_value(vulkan, cls, length):
    with pytest.raises(ValueError):
        cls(length)


@pytest.mark.parametrize("cls", BASIC_USABLE_BUFFER_CLS)
@pytest.mark.parametrize("length", [1.5, "123", b"abc"])
def test_length_initialize_invalid_type(vulkan, cls, length):
    with pytest.raises(TypeError):
        cls(length)


@pytest.mark.parametrize("cls", USABLE_BUFFER_CLS)
@pytest.mark.parametrize("length", [1, 100])
def test_length_initialize(vulkan, cls, length):
    g_buffer = cls(length)
    assert len(g_buffer) == length


@pytest.mark.parametrize("cls", (*WRITE_USABLE_BUFFER_CLS, *READ_WRITE_USABLE_BUFFER_CLS))
@pytest.mark.parametrize("buffer", [b""])
def test_buffer_initialize_invalid_value(vulkan, cls, buffer):
    with pytest.raises(ValueError):
        cls(buffer)


@pytest.mark.parametrize("cls", (*WRITE_USABLE_BUFFER_CLS, *READ_WRITE_USABLE_BUFFER_CLS))
@pytest.mark.parametrize("buffer", [1.5, "123", object()])
def test_buffer_initialize_invalid_type(vulkan, cls, buffer):
    with pytest.raises(TypeError):
        cls(buffer)


@pytest.mark.parametrize("cls", (*WRITE_USABLE_BUFFER_CLS, *READ_WRITE_USABLE_BUFFER_CLS))
@pytest.mark.parametrize("buffer", [b"\x00", b"\x00" * 100])
def test_buffer_initialize(vulkan, cls, buffer):
    g_buffer = cls(buffer)
    assert len(g_buffer) == len(buffer)


@pytest.mark.parametrize("cls", (*WRITE_USABLE_BUFFER_CLS, *READ_WRITE_USABLE_BUFFER_CLS))
def test_write(vulkan, cls):
    g_buffer = cls(b"123")
    with pytest.raises(ValueError) as excinfo:
        g_buffer.write(b"a", offset=-1)
    assert str(excinfo.value) == "underflow"
    g_buffer.write(b"a")
    g_buffer.write(b"ab")
    g_buffer.write(b"abc")
    with pytest.raises(ValueError) as excinfo:
        g_buffer.write(b"abcd")
    assert str(excinfo.value) == "overflow"
    g_buffer.write(b"a", offset=1)
    g_buffer.write(b"ab", offset=1)
    with pytest.raises(ValueError) as excinfo:
        g_buffer.write(b"abc", offset=1)
    assert str(excinfo.value) == "overflow"
    g_buffer.write(b"a", offset=2)
    with pytest.raises(ValueError) as excinfo:
        g_buffer.write(b"ab", offset=2)
    assert str(excinfo.value) == "overflow"
    with pytest.raises(ValueError) as excinfo:
        g_buffer.write(b"a", offset=3)
    assert str(excinfo.value) == "overflow"
    g_buffer.write(b"")
    g_buffer.write(b"", offset=-1)
    g_buffer.write(b"", offset=3)


@pytest.mark.parametrize("cls", READ_WRITE_USABLE_BUFFER_CLS)
def test_buffer_protocol(vulkan, cls):
    g_buffer = cls(b"123")
    b = memoryview(g_buffer)
    assert bytes(b) == b"123"
    b[0] = ord(b"a")
    assert bytes(b) == b"a23"
    g_buffer.flush()
    del b
    gc.collect()
    assert bytes(g_buffer) == b"a23"
