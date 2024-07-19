# egraphics
from egraphics import GBuffer
from egraphics._g_buffer import _reset_g_buffer_target_state

# emath
from emath import FVector3

# pyopengl
from OpenGL.GL import GL_ARRAY_BUFFER
from OpenGL.GL import GL_ARRAY_BUFFER_BINDING
from OpenGL.GL import GL_BUFFER_SIZE
from OpenGL.GL import GL_BUFFER_USAGE
from OpenGL.GL import GL_COPY_READ_BUFFER_BINDING
from OpenGL.GL import GL_DYNAMIC_COPY
from OpenGL.GL import GL_DYNAMIC_DRAW
from OpenGL.GL import GL_DYNAMIC_READ
from OpenGL.GL import GL_STATIC_COPY
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_STATIC_READ
from OpenGL.GL import GL_STREAM_COPY
from OpenGL.GL import GL_STREAM_DRAW
from OpenGL.GL import GL_STREAM_READ
from OpenGL.GL import glGetBufferParameteriv
from OpenGL.GL import glGetIntegerv
from OpenGL.GL import glIsBuffer

# pytest
import pytest


def test_defaults(platform):
    g_buffer = GBuffer()
    assert len(g_buffer) == 0
    assert bytes(g_buffer) == b""
    GBuffer.Target.ARRAY.g_buffer = g_buffer
    usage = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_USAGE)[0]
    assert usage == GL_STATIC_DRAW


@pytest.mark.parametrize("data", [0, b"", b"sdfsfsf", FVector3(0, 1, 2)])
@pytest.mark.parametrize("frequency", GBuffer.Frequency)
@pytest.mark.parametrize("nature", GBuffer.Nature)
def test_init(platform, data, frequency, nature):
    expected_usage = {
        (GBuffer.Frequency.STREAM, GBuffer.Nature.DRAW): GL_STREAM_DRAW,
        (GBuffer.Frequency.STREAM, GBuffer.Nature.READ): GL_STREAM_READ,
        (GBuffer.Frequency.STREAM, GBuffer.Nature.COPY): GL_STREAM_COPY,
        (GBuffer.Frequency.STATIC, GBuffer.Nature.DRAW): GL_STATIC_DRAW,
        (GBuffer.Frequency.STATIC, GBuffer.Nature.READ): GL_STATIC_READ,
        (GBuffer.Frequency.STATIC, GBuffer.Nature.COPY): GL_STATIC_COPY,
        (GBuffer.Frequency.DYNAMIC, GBuffer.Nature.DRAW): GL_DYNAMIC_DRAW,
        (GBuffer.Frequency.DYNAMIC, GBuffer.Nature.READ): GL_DYNAMIC_READ,
        (GBuffer.Frequency.DYNAMIC, GBuffer.Nature.COPY): GL_DYNAMIC_COPY,
    }[(frequency, nature)]
    if isinstance(data, int):
        expected_size = data
        expected_bytes = None
    else:
        expected_bytes = bytes(data)
        expected_size = len(expected_bytes)

    g_buffer = GBuffer(data, frequency=frequency, nature=nature)
    assert g_buffer._gl_buffer is not None
    assert glIsBuffer(g_buffer._gl_buffer)
    assert g_buffer.frequency == frequency
    assert g_buffer.nature == nature
    if expected_bytes is not None:
        assert bytes(g_buffer) == expected_bytes
    else:
        assert len(bytes(g_buffer)) == expected_size
    assert len(g_buffer) == expected_size

    GBuffer.Target.ARRAY.g_buffer = g_buffer
    usage = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_USAGE)[0]
    assert usage == expected_usage
    size = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)
    assert size == expected_size


@pytest.mark.parametrize("data", [-100, -1])
def test_invalid_init_length(platform, data):
    with pytest.raises(ValueError) as excinfo:
        GBuffer(data)
    assert str(excinfo.value) == "data must be 0 or more"


def test_destroy_buffer(platform):
    g_buffer = GBuffer(0)
    gl_buffer = g_buffer._gl_buffer
    del g_buffer
    assert not glIsBuffer(gl_buffer)


def test_buffer_protocol(platform):
    g_buffer = GBuffer(b"123")
    mv1 = memoryview(g_buffer)
    mv2 = memoryview(g_buffer)
    assert mv1 is not mv2
    assert bytes(mv1) == b"123"
    assert bytes(mv2) == b"123"
    mv1[0] = ord("a")
    assert bytes(mv1) == b"a23"
    assert bytes(mv2) == b"a23"
    mv2[:] = b"456"
    assert bytes(mv1) == b"456"
    assert bytes(mv2) == b"456"
    del mv1
    del mv2
    mv3 = memoryview(g_buffer)
    assert bytes(mv3) == b"456"


def test_buffer_protocol_0(platform):
    g_buffer = GBuffer(0)
    mv = memoryview(g_buffer)
    assert bytes(mv) == b""


@pytest.mark.parametrize(
    "name, buffer_binding",
    [
        ("ARRAY", GL_ARRAY_BUFFER_BINDING),
        ("COPY_READ", GL_COPY_READ_BUFFER_BINDING),
    ],
)
def test_g_buffer_target_default_state(platform, name, buffer_binding):
    target = getattr(GBuffer.Target, name)
    target.g_buffer is None
    assert glGetIntegerv(buffer_binding) == 0


@pytest.mark.parametrize(
    "name, buffer_binding",
    [
        ("ARRAY", GL_ARRAY_BUFFER_BINDING),
        ("COPY_READ", GL_COPY_READ_BUFFER_BINDING),
    ],
)
def test_g_buffer_target_set_g_buffer(platform, name, buffer_binding):
    g_buffer = GBuffer(0)

    target = getattr(GBuffer.Target, name)
    target.g_buffer = g_buffer
    assert glGetIntegerv(buffer_binding) == g_buffer._gl_buffer

    target.g_buffer = None
    assert glGetIntegerv(buffer_binding) == 0


def test_g_buffer_reset(platform):
    g_buffer = GBuffer(0)
    GBuffer.Target.ARRAY.g_buffer = g_buffer
    GBuffer.Target.COPY_READ.g_buffer = g_buffer

    _reset_g_buffer_target_state()
    assert GBuffer.Target.ARRAY.g_buffer is None
    assert glGetIntegerv(GL_ARRAY_BUFFER_BINDING) == 0
    assert GBuffer.Target.COPY_READ.g_buffer is None
    assert glGetIntegerv(GL_COPY_READ_BUFFER_BINDING) == 0
