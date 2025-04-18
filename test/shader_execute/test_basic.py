# egraphics
from egraphics import GBuffer
from egraphics import GBufferView
from egraphics import GBufferViewMap
from egraphics import PrimitiveMode
from egraphics import Shader
from egraphics import clear_render_target
from egraphics import read_color_from_render_target

# egeometry
from egeometry import IRectangle

# emath
from emath import FVector2
from emath import FVector2Array
from emath import FVector3
from emath import FVector4
from emath import IVector2
from emath import U8Array
from emath import U16Array
from emath import U32Array

# pytest
import pytest

# python
import ctypes
from pathlib import Path

DIR = Path(__file__).parent


def test_not_a_uniform(render_target):
    shader = Shader(
        vertex=b"""
        #version 140
        in vec2 xy;
        void main()
        {
            gl_Position = vec4(xy, 0, 1.0);
        }
        """,
    )
    with pytest.raises(ValueError) as excinfo:
        shader.execute(
            render_target,
            PrimitiveMode.POINT,
            GBufferViewMap(
                {
                    "xy": GBufferView.from_array(
                        FVector2Array(
                            FVector2(-0.9, -0.9),
                            FVector2(-0.9, 0.9),
                            FVector2(0.9, 0.9),
                            FVector2(0.9, -0.9),
                        )
                    )
                },
                (0, 4),
            ),
            {"color": FVector4()},
        )
    assert str(excinfo.value) == ('shader does not accept a uniform called "color"')


def test_missing_uniform(render_target):
    shader = Shader(
        vertex=b"""
        #version 140
        in vec2 xy;
        uniform float z;
        void main()
        {
            gl_Position = vec4(xy, z, 1.0);
        }
        """
    )
    with pytest.raises(ValueError) as excinfo:
        shader.execute(
            render_target,
            PrimitiveMode.POINT,
            GBufferViewMap(
                {
                    "xy": GBufferView.from_array(
                        FVector2Array(
                            FVector2(-0.9, -0.9),
                            FVector2(-0.9, 0.9),
                            FVector2(0.9, 0.9),
                            FVector2(0.9, -0.9),
                        )
                    )
                },
                (0, 4),
            ),
            {},
        )
    assert str(excinfo.value) == "missing uniform: z"


def test_not_an_attribute(render_target):
    shader = Shader(
        vertex=b"""
        #version 140
        void main()
        {
            gl_Position = vec4(0, 0, 0, 1.0);
        }
        """,
    )
    with pytest.raises(ValueError) as excinfo:
        shader.execute(
            render_target,
            PrimitiveMode.POINT,
            GBufferViewMap(
                {
                    "xy": GBufferView.from_array(
                        FVector2Array(
                            FVector2(-0.9, -0.9),
                            FVector2(-0.9, 0.9),
                            FVector2(0.9, 0.9),
                            FVector2(0.9, -0.9),
                        )
                    )
                },
                (0, 4),
            ),
            {},
        )
    assert str(excinfo.value) == ('shader does not accept an attribute called "xy"')


def test_missing_attribute(render_target):
    shader = Shader(
        vertex=b"""
        #version 140
        in vec2 xy;
        in float z;
        void main()
        {
            gl_Position = vec4(xy, z, 1.0);
        }
        """,
    )
    with pytest.raises(ValueError) as excinfo:
        shader.execute(
            render_target,
            PrimitiveMode.POINT,
            GBufferViewMap(
                {
                    "xy": GBufferView.from_array(
                        FVector2Array(
                            FVector2(-0.9, -0.9),
                            FVector2(-0.9, 0.9),
                            FVector2(0.9, 0.9),
                            FVector2(0.9, -0.9),
                        )
                    )
                },
                (0, 4),
            ),
            {},
        )
    assert str(excinfo.value) == "missing attribute: z"


@pytest.mark.parametrize("primitive_mode", list(PrimitiveMode))
@pytest.mark.parametrize(
    "color",
    [
        FVector4(1, 1, 1, 1),
        FVector4(1, 0, 0, 1),
        FVector4(0, 1, 0, 1),
        FVector4(0, 0, 1, 1),
    ],
)
@pytest.mark.parametrize(
    "index_array_type", [None, U8Array, U16Array, U32Array, "length", "offset"]
)
def test_basic(render_target, primitive_mode, color, index_array_type):
    clear_render_target(render_target, color=FVector3(0, 0, 0), depth=True)

    if index_array_type is None:
        indices = (0, 4)
    elif index_array_type == "length":
        indices = GBufferView(GBuffer(U8Array(0, 1, 2, 3, 4)), ctypes.c_uint8, length=4)
    elif index_array_type == "offset":
        indices = GBufferView(GBuffer(U8Array(4, 0, 1, 2, 3)), ctypes.c_uint8, offset=1)
    else:
        indices = GBufferView.from_array(
            index_array_type(
                0,
                1,
                2,
                3,
            )
        )

    shader = Shader(
        vertex=b"""
        #version 140
        in vec2 xy;
        out vec4 color_mult;
        void main()
        {
            color_mult = vec4(1);
            if (gl_VertexID == 4)
            {
                color_mult = vec4(.5);
            }
            gl_Position = vec4(xy, 0, 1.0);
        }
        """,
        fragment=b"""
        #version 140
        uniform vec4 color;
        in vec4 color_mult;
        out vec4 FragColor;
        void main()
        {
            FragColor = color * color_mult;
        }
        """,
    )
    shader.execute(
        render_target,
        primitive_mode,
        GBufferViewMap(
            {
                "xy": GBufferView.from_array(
                    FVector2Array(
                        FVector2(-0.9, -0.9),
                        FVector2(-0.9, 0.9),
                        FVector2(0.9, 0.9),
                        FVector2(0.9, -0.9),
                        FVector2(1, 1),
                    )
                )
            },
            indices,
        ),
        {"color": color},
    )

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, 0), render_target.size)
    )

    assert color in colors
    assert FVector4(0, 0, 0, 1) in colors
    assert len(set(colors)) == 2
