# egraphics
from egraphics import GBufferView
from egraphics import GBufferViewMap
from egraphics import PrimitiveMode
from egraphics import Shader
from egraphics import clear_render_target
from egraphics import read_color_from_render_target

# egeometry
from egeometry import IBoundingBox2d
from egeometry import IRectangle

# emath
from emath import FVector2
from emath import FVector2Array
from emath import FVector3
from emath import FVector4
from emath import IVector2

# pytest
import pytest

# python
from pathlib import Path
import sys

DIR = Path(__file__).parent


@pytest.mark.xfail(sys.platform == "darwin", reason="not sure")
@pytest.mark.parametrize("pixel", ["top-left", "top-right", "bottom-right", "bottom-left"])
def test_basic(render_target, pixel):
    if pixel == "top-right":
        scissor = IBoundingBox2d(render_target.size.xo - IVector2(1, 0), IVector2(1))
        pixel_changed = (render_target.size.x * render_target.size.y) - 1
    elif pixel == "top-left":
        scissor = IBoundingBox2d(IVector2(0), IVector2(1))
        pixel_changed = (render_target.size.x * render_target.size.y) - render_target.size.x
    elif pixel == "bottom-right":
        scissor = IBoundingBox2d(render_target.size - IVector2(1), IVector2(1))
        pixel_changed = render_target.size.x - 1
    elif pixel == "bottom-left":
        scissor = IBoundingBox2d(render_target.size.oy - IVector2(0, 1), IVector2(1))
        pixel_changed = 0

    clear_render_target(render_target, color=FVector3(0, 0, 0), depth=True)
    color = FVector4(1, 1, 1, 1)
    shader = Shader(
        vertex=b"""
        #version 140
        in vec2 xy;
        void main()
        {
            gl_Position = vec4(xy, 0, 1.0);
        }
        """,
        fragment=b"""
        #version 140
        uniform vec4 color;
        out vec4 FragColor;
        void main()
        {
            FragColor = color;
        }
        """,
    )
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
        {"color": color},
        scissor=scissor,
    )

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, 0), render_target.size)
    )
    for c in colors:
        print(c)
    assert colors[pixel_changed] == color
    assert all((c != color for c in (colors[:pixel_changed], colors[pixel_changed + 1 :])))
