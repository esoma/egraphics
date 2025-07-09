import struct

from egeometry import IRectangle
from emath import FMatrix4
from emath import FVector2
from emath import FVector4
from emath import IVector2

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
in mat4 sentinel;
void main()
{
    vec2 pos = xy;
    if (sentinel != mat4(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
    {
        pos = vec2(-999, -999);
    }
    gl_Position = vec4(pos, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = b"""
#version 140
out vec4 FragColor;
void main()
{
    FragColor = vec4(1);
}
"""


def draw_fullscreen_quad(render_target, shader):
    format = "ffffffffffffffffff"
    g_buffer = GBuffer(
        b"".join(
            struct.pack(format, x, y, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
            for x, y in ((-1, -1), (-1, 1), (1, 1), (1, -1))
        )
    )
    shader.execute(
        render_target,
        PrimitiveMode.TRIANGLE_FAN,
        GBufferViewMap(
            {
                "xy": GBufferView(g_buffer, FVector2, stride=struct.calcsize(format)),
                "sentinel": GBufferView(
                    g_buffer,
                    FMatrix4,
                    offset=struct.calcsize("ff"),
                    stride=struct.calcsize(format),
                ),
            },
            (0, 4),
        ),
        {},
    )


def test_stride_offset(render_target):
    clear_render_target(render_target, color=FVector4(0, 0, 0, 1))

    shader = Shader(vertex=VERTEX_SHADER, fragment=FRAGMENT_SHADER)

    draw_fullscreen_quad(render_target, shader)

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0), render_target.size)
    )
    assert all(c.r == 1 and c.g == 1 and c.b == 1 for c in colors)
