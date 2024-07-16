# egraphics
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

# eplatform
from eplatform import Window

# pytest
import pytest

# python
from io import BytesIO

VERTEX_SHADER = b"""
#version 140
in vec2 xy;
void main()
{
    gl_Position = vec4(xy, 0.0, 1.0);
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
    shader,
    color,
    color_write,
):
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
        },
        color_write=color_write,
    )


@pytest.mark.parametrize("red", [True, False])
@pytest.mark.parametrize("green", [True, False])
@pytest.mark.parametrize("blue", [True, False])
@pytest.mark.parametrize("alpha", [True, False])
def test_mask(render_target, red, green, blue, alpha):
    clear_render_target(render_target, color=FVector3(0, 0, 0))

    shader = Shader(vertex=BytesIO(VERTEX_SHADER), fragment=BytesIO(FRAGMENT_SHADER))

    draw_fullscreen_quad(
        render_target, shader, FVector4(0.2, 0.4, 0.6, 0.8), (red, green, blue, alpha)
    )

    expected_color = FVector4(
        0.2 if red else 0, 0.4 if green else 0, 0.6 if blue else 0, 0.8 if alpha else 1
    )
    ignore_alpha = isinstance(render_target, Window)

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
