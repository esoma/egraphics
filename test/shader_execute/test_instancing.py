from itertools import permutations

import pytest
from egeometry import IRectangle
from emath import FVector2
from emath import FVector2Array
from emath import FVector3
from emath import FVector3Array
from emath import FVector4
from emath import IVector2
from eplatform import Window

from egraphics import GBuffer
from egraphics import GBufferView
from egraphics import GBufferViewMap
from egraphics import PrimitiveMode
from egraphics import Shader
from egraphics import clear_render_target
from egraphics import read_color_from_render_target

VERTEX_SHADER = b"""
#version 140
in vec2 xy;
in vec3 instance_color;
out vec3 vertex_color;
void main()
{
    vertex_color = instance_color;
    gl_Position = vec4(xy, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = b"""
#version 140
in vec3 vertex_color;
out vec4 FragColor;
void main()
{
    FragColor = vec4(vertex_color, 1);
}
"""


def draw_fullscreen_quads(render_target, shader, colors):
    shader.execute(
        render_target,
        PrimitiveMode.TRIANGLE_FAN,
        GBufferViewMap(
            {
                "xy": GBufferView.from_array(
                    FVector2Array(
                        FVector2(-1, -1), FVector2(-1, 1), FVector2(1, 1), FVector2(1, -1)
                    )
                ),
                "instance_color": GBufferView.from_array(
                    FVector3Array(*colors) if colors else FVector3Array(), instancing_divisor=1
                ),
            },
            (0, 4),
        ),
        {},
        instances=len(colors),
    )


def test_negative_instances(render_target):
    shader = Shader(vertex=VERTEX_SHADER, fragment=FRAGMENT_SHADER)
    with pytest.raises(ValueError) as excinfo:
        shader.execute(
            render_target,
            PrimitiveMode.TRIANGLE_FAN,
            GBufferViewMap(
                {
                    "xy": GBufferView(GBuffer(), FVector2),
                    "instance_color": GBufferView(GBuffer(), FVector3),
                },
                (0, 4),
            ),
            {},
            instances=-1,
        )
    assert str(excinfo.value) == "instances must be 0 or more"


def test_zero_instances(render_target):
    clear_render_target(render_target, color=FVector4(0, 0, 0, 1))
    shader = Shader(vertex=VERTEX_SHADER, fragment=FRAGMENT_SHADER)
    draw_fullscreen_quads(render_target, shader, [])

    expected_color = FVector4(0, 0, 0, 1)
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


@pytest.mark.parametrize(
    "colors",
    permutations([FVector3(1, 1, 1), FVector3(1, 0, 0), FVector3(0, 1, 0), FVector3(0, 0, 1)]),
)
def test_basic(render_target, colors) -> None:
    clear_render_target(render_target, color=FVector4(0))

    shader = Shader(vertex=VERTEX_SHADER, fragment=FRAGMENT_SHADER)

    draw_fullscreen_quads(render_target, shader, colors)

    expected_color = FVector4(*colors[-1], 1)
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
