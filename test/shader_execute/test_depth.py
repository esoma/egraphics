# egraphics
from egraphics import DepthTest
from egraphics import GBufferView
from egraphics import GBufferViewMap
from egraphics import PrimitiveMode
from egraphics import Shader
from egraphics import clear_render_target
from egraphics import read_color_from_render_target
from egraphics import read_depth_from_render_target

# egeometry
from egeometry import IRectangle

# emath
from emath import FVector2
from emath import FVector2Array
from emath import FVector3
from emath import FVector4
from emath import IVector2

# eplatform
from eplatform import Window

# pytest
import pytest

# python
import ctypes
from io import BytesIO

VERTEX_SHADER = b"""
#version 140
in vec2 xy;
uniform float depth;
void main()
{
    gl_Position = vec4(xy, depth, 1.0);
}
"""

FRAGMENT_SHADER = b"""
#version 140
uniform vec4 color;
out vec4 FragColor;
void main()
{
    FragColor = color;
}
"""


def draw_fullscreen_quad(
    render_target,
    shader: Shader,
    color: FVector4,
    depth: float,
    depth_test: DepthTest,
    depth_write: bool,
) -> None:
    shader.execute(
        render_target,
        PrimitiveMode.TRIANGLE_FAN,
        GBufferViewMap(
            {
                "xy": GBufferView.from_array(
                    FVector2Array(
                        FVector2(-1, -1),
                        FVector2(-1, 1),
                        FVector2(1, 1),
                        FVector2(1, -1),
                    )
                )
            },
            (0, 4),
        ),
        {
            "color": color,
            "depth": ctypes.c_float(depth),
        },
        depth_test=depth_test,
        depth_write=depth_write,
    )


@pytest.mark.parametrize(
    "depth_test, depth_write, expected_color, expected_depth",
    [
        (DepthTest.ALWAYS, False, FVector4(0, 0, 1, 1), 0.5),
        (DepthTest.ALWAYS, True, FVector4(0, 0, 1, 1), 0.25),
        (DepthTest.NEVER, False, FVector4(0, 0, 0, 1), 0.5),
        (DepthTest.NEVER, True, FVector4(0, 0, 0, 1), 0.5),
        (DepthTest.LESS, False, FVector4(0, 0, 1, 1), 0.5),
        (DepthTest.LESS, True, FVector4(1, 1, 0, 1), 0.125),
        (DepthTest.LESS_EQUAL, False, FVector4(0, 0, 1, 1), 0.5),
        (DepthTest.LESS_EQUAL, True, FVector4(0, 1, 1, 1), 0.125),
        (DepthTest.GREATER, False, FVector4(0, 1, 0, 1), 0.5),
        (DepthTest.GREATER, True, FVector4(1, 1, 1, 1), 1.0),
        (DepthTest.GREATER_EQUAL, False, FVector4(0.5, 0.5, 0.5, 1), 0.5),
        (DepthTest.GREATER_EQUAL, True, FVector4(1, 0, 0, 1), 1.0),
        (DepthTest.EQUAL, False, FVector4(0.5, 0.5, 0.5, 1), 0.5),
        (DepthTest.EQUAL, True, FVector4(0.5, 0.5, 0.5, 1), 0.5),
        (DepthTest.NOT_EQUAL, False, FVector4(0, 0, 1, 1), 0.5),
        (DepthTest.NOT_EQUAL, True, FVector4(0.1, 0.1, 0.1, 1), 0.25),
    ],
)
def test_basic(render_target, depth_test, depth_write, expected_color, expected_depth):
    ignore_alpha = isinstance(render_target, Window)
    clear_render_target(render_target, color=FVector3(0, 0, 0), depth=0.5)

    shader = Shader(vertex=BytesIO(VERTEX_SHADER), fragment=BytesIO(FRAGMENT_SHADER))

    def test_draw_fullscreen_quad(color, depth):
        draw_fullscreen_quad(render_target, shader, color, depth, depth_test, depth_write)

    test_draw_fullscreen_quad(FVector4(1, 1, 1, 1), 1)
    test_draw_fullscreen_quad(FVector4(1, 0, 0, 1), 1)
    test_draw_fullscreen_quad(FVector4(0, 1, 0, 1), 0.25)
    test_draw_fullscreen_quad(FVector4(0.5, 0.5, 0.5, 1), 0)
    test_draw_fullscreen_quad(FVector4(1, 1, 0, 1), -0.75)
    test_draw_fullscreen_quad(FVector4(0, 1, 1, 1), -0.75)
    test_draw_fullscreen_quad(FVector4(0.1, 0.1, 0.1, 1), -0.5)
    test_draw_fullscreen_quad(FVector4(0, 0, 1, 1), -0.5)

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0), render_target.size)
    )
    assert all(
        c.r == pytest.approx(expected_color[0], abs=0.01)
        and c.g == pytest.approx(expected_color[1], abs=0.01)
        and c.b == pytest.approx(expected_color[2], abs=0.01)
        and (ignore_alpha or c.a == pytest.approx(expected_color[3], abs=0.01))
        for c in colors
    )

    depths = read_depth_from_render_target(
        render_target, IRectangle(IVector2(0), render_target.size)
    )
    print(depths[0], expected_depth)
    assert all(d == pytest.approx(expected_depth, abs=1e-6) for d in depths)
