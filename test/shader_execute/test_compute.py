import ctypes

import pytest
from egeometry import IRectangle
from emath import FVector2
from emath import FVector2Array
from emath import FVector3
from emath import FVector4
from emath import IVector2

from egraphics import ComputeShader
from egraphics import GBuffer
from egraphics import GBufferView
from egraphics import GBufferViewMap
from egraphics import PrimitiveMode
from egraphics import Shader
from egraphics import Texture2d
from egraphics import TextureComponents
from egraphics import clear_cache
from egraphics import clear_render_target
from egraphics import read_color_from_render_target


def test_compute(render_target, gl_version, is_kinda_close):
    if gl_version < (4, 3):
        pytest.xfail()

    size = render_target.size
    clear_render_target(render_target, color=FVector4(0, 0, 0, 1), depth=True)

    compute_texture = Texture2d(
        size.to_u(), TextureComponents.XYZW, ctypes.c_float, b"\x00" * (4 * 4 * size.x * size.y)
    )

    ssbo_buffer = GBuffer(ctypes.sizeof(ctypes.c_float) * 4 * size.x * size.y)
    ssbo_view = GBufferView(ssbo_buffer, FVector3, stride=ctypes.sizeof(ctypes.c_float) * 4)

    compute_shader = ComputeShader(
        compute=f"""#version 430 core
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
layout (rgba32f) uniform image2D result;
layout(std430) buffer ColorBuffer
{{
    vec3 rgb[];
}} color_buffer;

void main()
{{
    ivec2 coord = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(result);

    if (coord.x >= size.x || coord.y >= size.y)
    {{
        return;
    }}

    float red = float(coord.x) / float(size.x - 1);
    float green = float(coord.y) / float(size.y - 1);

    imageStore(result, coord, vec4(red, green, 0.0, 1.0));
    color_buffer.rgb[
        gl_GlobalInvocationID.y * size.x + gl_GlobalInvocationID.x
    ] = vec3(red, green, 1);
}}
""".encode("utf-8")
    )

    compute_shader.execute(
        {"result": compute_texture, "ColorBuffer": ssbo_view}, size.x, size.y, 1
    )

    clear_cache(shader_image=True, shader_texture=True, g_buffer=True)

    render_shader = Shader(
        vertex=b"""
        #version 140
        in vec2 xy;
        in vec2 uv;
        out vec2 tex_coord;
        void main()
        {
            tex_coord = uv;
            gl_Position = vec4(xy, 0, 1.0);
        }
        """,
        fragment=b"""
        #version 140
        uniform sampler2D tex;
        in vec2 tex_coord;
        out vec4 FragColor;
        void main()
        {
            FragColor = texture(tex, tex_coord);
        }
        """,
    )
    render_shader.execute(
        render_target,
        PrimitiveMode.TRIANGLE_FAN,
        GBufferViewMap(
            {
                "xy": GBufferView.from_array(
                    FVector2Array(
                        FVector2(-1, -1), FVector2(-1, 1), FVector2(1, 1), FVector2(1, -1)
                    )
                ),
                "uv": GBufferView.from_array(
                    FVector2Array(FVector2(0, 0), FVector2(0, 1), FVector2(1, 1), FVector2(1, 0))
                ),
            },
            (0, 4),
        ),
        {"tex": compute_texture},
    )

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0, 0), render_target.size)
    )
    buffer_colors = list(GBufferView(ssbo_buffer, FVector4))
    for y in range(size.y):
        for x in range(size.x):
            i = y * size.x + x
            color = colors[i]
            expected_red = x / (size.x - 1) if size.x > 1 else 0.0
            expected_green = y / (size.y - 1) if size.y > 1 else 0.0
            assert is_kinda_close(color.r, expected_red)
            assert is_kinda_close(color.g, expected_green)
            assert is_kinda_close(color.b, 0.0)
            assert is_kinda_close(color.a, 1.0)
            buffer_color = buffer_colors[i]
            assert is_kinda_close(buffer_color.r, expected_red)
            assert is_kinda_close(buffer_color.g, expected_green)
            assert is_kinda_close(buffer_color.b, 1.0)
