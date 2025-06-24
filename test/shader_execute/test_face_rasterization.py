import pytest
from egeometry import IRectangle
from emath import FVector2
from emath import FVector2Array
from emath import FVector4
from emath import IVector2
from emath import U8Array

from egraphics import FaceRasterization
from egraphics import GBufferView
from egraphics import GBufferViewMap
from egraphics import PrimitiveMode
from egraphics import Shader
from egraphics import clear_render_target
from egraphics import read_color_from_render_target


@pytest.mark.parametrize("face_rasterization", FaceRasterization)
def test_face_rasterization(render_target, face_rasterization):
    clear_render_target(render_target, color=FVector4(0, 0, 0, 1), depth=True)
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

    d = FVector2(0)
    if face_rasterization != FaceRasterization.FILL:
        d = FVector2(1) / FVector2(*render_target.size)

    shader.execute(
        render_target,
        PrimitiveMode.TRIANGLE,
        GBufferViewMap(
            {
                "xy": GBufferView.from_array(
                    FVector2Array(
                        FVector2(-1 + d.x, -1 + d.y),
                        FVector2(-1 + d.x, 1 - d.y),
                        FVector2(1 - d.x, 1 - d.y),
                        FVector2(1 - d.x, -1 + d.x),
                    )
                )
            },
            GBufferView.from_array(U8Array(0, 1, 2, 2, 0, 3)),
        ),
        {},
        face_rasterization=face_rasterization,
    )

    top_left = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, 0), IVector2(1, 1))
    )[0]
    assert top_left == FVector4(1)
    top_right = read_color_from_render_target(
        render_target, IRectangle(IVector2(render_target.size.x - 1, 0), IVector2(1, 1))
    )[0]
    assert top_right == FVector4(1)
    bottom_right = read_color_from_render_target(
        render_target, IRectangle(render_target.size - IVector2(1, 1), IVector2(1, 1))
    )[0]
    assert bottom_right == FVector4(1)
    bottom_left = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, render_target.size.y - 1), IVector2(1, 1))
    )[0]
    assert bottom_left == FVector4(1)

    top = read_color_from_render_target(
        render_target, IRectangle(IVector2(render_target.size.x // 2, 0), IVector2(1, 1))
    )[0]
    bottom = read_color_from_render_target(
        render_target,
        IRectangle(IVector2(render_target.size.x // 2, render_target.size.y - 1), IVector2(1, 1)),
    )[0]
    left = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, render_target.size.y // 2), IVector2(1, 1))
    )[0]
    right = read_color_from_render_target(
        render_target,
        IRectangle(IVector2(render_target.size.x - 1, render_target.size.y // 2), IVector2(1, 1)),
    )[0]
    if face_rasterization == FaceRasterization.POINT:
        assert top == FVector4(0, 0, 0, 1)
        assert bottom == FVector4(0, 0, 0, 1)
        assert left == FVector4(0, 0, 0, 1)
        assert right == FVector4(0, 0, 0, 1)
    else:
        assert top == FVector4(1)
        assert bottom == FVector4(1)
        assert left == FVector4(1)
        assert right == FVector4(1)

    mid_top_right = read_color_from_render_target(
        render_target,
        IRectangle(
            IVector2((render_target.size.x // 4) * 3, render_target.size.y // 4), IVector2(1, 1)
        ),
    )[0]
    mid_bottom_left = read_color_from_render_target(
        render_target,
        IRectangle(
            IVector2(render_target.size.x // 4, (render_target.size.y // 4) * 3), IVector2(1, 1)
        ),
    )[0]
    if face_rasterization == FaceRasterization.FILL:
        assert mid_top_right == FVector4(1)
        assert mid_bottom_left == FVector4(1)
    else:
        assert mid_top_right == FVector4(0, 0, 0, 1)
        assert mid_bottom_left == FVector4(0, 0, 0, 1)
