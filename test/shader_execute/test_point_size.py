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
from emath import FVector4
from emath import IVector2

# pytest
import pytest

# python
from collections import Counter
from pathlib import Path

DIR = Path(__file__).parent


@pytest.mark.parametrize("point_size", [None, 1.0, 2.0, 4.0, 8.0])
def test_point_size(render_target, point_size):
    clear_render_target(render_target, color=FVector4(0), depth=True)

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
        out vec4 FragColor;
        void main()
        {
            FragColor = vec4(1);
        }
        """,
    )

    kwargs = {}
    if point_size is not None:
        kwargs["point_size"] = point_size
    else:
        point_size = 1.0

    shader.execute(
        render_target,
        PrimitiveMode.POINT,
        GBufferViewMap(
            {"xy": GBufferView.from_array(FVector2Array(FVector2(0, 0)))},
            (0, 1),
        ),
        {},
        **kwargs,
    )

    rect = IRectangle(IVector2(0, 0), IVector2(render_target.size[0], render_target.size[1]))
    colors = read_color_from_render_target(render_target, rect)
    color_counts = Counter(colors)

    assert color_counts[FVector4(1, 1, 1, 1)] == point_size * point_size
