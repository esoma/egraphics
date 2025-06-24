# egraphics
from egraphics import FaceCull
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
from emath import FVector4
from emath import IVector2

# eplatform
from eplatform import Window

# pytest
import pytest

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


def draw_fullscreen_quad(render_target, shader, color, front, face_cull) -> None:
    xy = [
        FVector2(-1, -1),
        FVector2(-1, 1),
        FVector2(1, 1),
        FVector2(1, -1),
    ]
    shader.execute(
        render_target,
        PrimitiveMode.TRIANGLE_FAN,
        GBufferViewMap(
            {"xy": GBufferView.from_array(FVector2Array(*(reversed(xy) if front else xy)))}, (0, 4)
        ),
        {
            "color": color,
        },
        face_cull=face_cull,
    )


@pytest.mark.parametrize(
    "face_cull, expected_color",
    [
        (FaceCull.NONE, FVector4(0, 0, 1, 1)),
        (FaceCull.FRONT, FVector4(0, 1, 0, 1)),
        (FaceCull.BACK, FVector4(0, 0, 1, 1)),
    ],
)
def test_basic(render_target, face_cull, expected_color):
    ignore_alpha = isinstance(render_target, Window)
    clear_render_target(render_target, color=FVector4(0))

    shader = Shader(vertex=VERTEX_SHADER, fragment=FRAGMENT_SHADER)

    def test_draw_fullscreen_quad(color, front, face_cull) -> None:
        draw_fullscreen_quad(
            render_target,
            shader,
            color,
            front,
            face_cull,
        )

    test_draw_fullscreen_quad(FVector4(1, 0, 0, 1), True, face_cull)
    test_draw_fullscreen_quad(FVector4(0, 1, 0, 1), False, face_cull)
    test_draw_fullscreen_quad(FVector4(0, 0, 1, 1), True, face_cull)

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
