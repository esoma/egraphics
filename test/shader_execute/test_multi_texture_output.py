# egraphics
from egraphics import GBufferView
from egraphics import GBufferViewMap
from egraphics import PrimitiveMode
from egraphics import Shader
from egraphics import Texture2d
from egraphics import TextureComponents
from egraphics import TextureRenderTarget
from egraphics import clear_render_target
from egraphics import read_color_from_render_target

# egeometry
from egeometry import IRectangle

# emath
from emath import FVector2
from emath import FVector2Array
from emath import FVector4
from emath import IVector2
from emath import UVector2

# python
import ctypes
from pathlib import Path

DIR = Path(__file__).parent


def test_multi_texture_output(platform, is_kinda_close):
    colors_1 = Texture2d(
        UVector2(10), TextureComponents.RGBA, ctypes.c_uint8, b"\x00" * 4 * 10 * 10
    )
    colors_2 = Texture2d(
        UVector2(10), TextureComponents.RGBA, ctypes.c_uint8, b"\x00" * 4 * 10 * 10
    )
    render_target = TextureRenderTarget([colors_1, colors_2])
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
        #extension GL_ARB_explicit_attrib_location : enable
        uniform vec4 color_1;
        uniform vec4 color_2;
        layout(location = 0) out vec4 color_1_out;
        layout(location = 1) out vec4 color_2_out;
        void main()
        {
            color_1_out = color_1;
            color_2_out = color_2;
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
        {"color_1": FVector4(0.5, 0.5, 0.5, 1), "color_2": FVector4(0.75, 0.75, 0.75, 1)},
    )

    colors_1_data = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, 0), render_target.size)
    )
    assert all(
        is_kinda_close(p.r, 0.5) and is_kinda_close(p.g, 0.5) and is_kinda_close(p.b, 0.5)
        for p in colors_1_data
    )
    colors_2_data = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, 0), render_target.size), index=1
    )
    assert all(
        is_kinda_close(p.r, 0.75) and is_kinda_close(p.g, 0.75) and is_kinda_close(p.b, 0.75)
        for p in colors_2_data
    )
