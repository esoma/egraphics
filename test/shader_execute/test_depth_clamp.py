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
from emath import FArray
from emath import FVector3
from emath import FVector4
from emath import IVector2

# pytest
import pytest


@pytest.mark.parametrize(
    "z, is_rendered",
    [
        (-1.1, False),
        (-1, True),
        (0, True),
        (1, True),
        (1.1, False),
    ],
)
@pytest.mark.parametrize("depth_clamp_kwargs", [{}, {"depth_clamp": False}])
def test_no_clamp(render_target, z, is_rendered, depth_clamp_kwargs):
    clear_render_target(render_target, color=FVector3(0, 0, 0))
    shader = Shader(
        vertex=b"""
        #version 140
        in float z;
        void main()
        {
            gl_Position = vec4(0, 0, z, 1.0);
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
    shader.execute(
        render_target,
        PrimitiveMode.POINT,
        GBufferViewMap(
            {"z": GBufferView.from_array(FArray(z))},
            (0, 1),
        ),
        {},
        **depth_clamp_kwargs,
    )

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, 0), render_target.size)
    )
    assert (FVector4(1) in colors) == is_rendered


@pytest.mark.parametrize("z", [-1.1, -1.0, 0.0, 1.0, 1.1])
def test_clamp(render_target, z):
    clear_render_target(render_target, color=FVector3(0, 0, 0))
    shader = Shader(
        vertex=b"""
        #version 140
        in float z;
        void main()
        {
            gl_Position = vec4(0, 0, z, 1.0);
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
    shader.execute(
        render_target,
        PrimitiveMode.POINT,
        GBufferViewMap(
            {"z": GBufferView.from_array(FArray(z))},
            (0, 1),
        ),
        {},
        depth_clamp=True,
    )

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, 0), render_target.size)
    )
    assert FVector4(1) in colors
