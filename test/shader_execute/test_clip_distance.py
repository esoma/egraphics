import pytest
from egeometry import IRectangle
from emath import FVector2
from emath import FVector2Array
from emath import FVector4
from emath import IVector2

from egraphics import GBufferView
from egraphics import GBufferViewMap
from egraphics import PrimitiveMode
from egraphics import Shader
from egraphics import clear_render_target
from egraphics import read_color_from_render_target

FRAGMENT_SHADER = b"""
#version 140
out vec4 FragColor;
void main()
{
    FragColor = vec4(1);
}
"""


def draw_fullscreen_quad(render_target, clip_distances, clipped):
    set_clip_distances = "".join(
        f"gl_ClipDistance[{i}] = {-1 if clipped == i else 1};" for i in range(clip_distances)
    )
    vertex_shader = f"""
    #version 140
    in vec2 xy;
    void main()
    {{
        {set_clip_distances}
        gl_Position = vec4(xy, 0.0, 1.0);
    }}
    """.encode("utf8")

    shader = Shader(vertex=vertex_shader, fragment=FRAGMENT_SHADER)
    shader.execute(
        render_target,
        PrimitiveMode.TRIANGLE_FAN,
        GBufferViewMap(
            {
                "xy": GBufferView.from_array(
                    FVector2Array(
                        FVector2(-1, -1), FVector2(-1, 1), FVector2(1, 1), FVector2(1, -1)
                    )
                )
            },
            (0, 4),
        ),
        {},
        clip_distances=clip_distances,
    )


@pytest.mark.parametrize("clip_distances", [1, 8])
def test_clip_distance(render_target, clip_distances):
    clear_render_target(render_target, color=FVector4(0, 0, 0, 1))

    draw_fullscreen_quad(render_target, clip_distances, None)

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0), render_target.size)
    )
    assert all(c.r == 1 and c.g == 1 and c.b == 1 for c in colors)

    for i in range(clip_distances):
        clear_render_target(render_target, color=FVector4(0, 0, 0, 1))

        draw_fullscreen_quad(render_target, clip_distances, i)

        colors = read_color_from_render_target(
            render_target, IRectangle(IVector2(0), render_target.size)
        )
        assert all(c.r == 0 and c.g == 0 and c.b == 0 for c in colors)
