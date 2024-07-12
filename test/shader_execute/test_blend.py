# egraphics
from egraphics import BlendFactor
from egraphics import BlendFunction
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
from emath import FVector3
from emath import FVector4
from emath import IVector2

# eplatform
from eplatform import Window

# pytest
import pytest

# python
from io import BytesIO

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


def draw_fullscreen_quad(
    render_target,
    shader,
    color,
    blend_source,
    blend_destination,
    blend_source_alpha,
    blend_destination_alpha,
    blend_function,
    blend_color,
):
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
        {
            "color": color,
        },
        blend_source=blend_source,
        blend_destination=blend_destination,
        blend_source_alpha=blend_source_alpha,
        blend_destination_alpha=blend_destination_alpha,
        blend_function=blend_function,
        blend_color=blend_color,
    )


def calculate_factor(factor, source_color, destination_color, blend_color) -> FVector4:
    if factor == BlendFactor.ZERO:
        return FVector4(0)
    elif factor == BlendFactor.ONE:
        return FVector4(1)
    elif factor == BlendFactor.SOURCE_COLOR:
        return source_color
    elif factor == BlendFactor.ONE_MINUS_SOURCE_COLOR:
        return 1 - source_color
    elif factor == BlendFactor.DESTINATION_COLOR:
        return destination_color
    elif factor == BlendFactor.ONE_MINUS_DESTINATION_COLOR:
        return 1 - destination_color
    elif factor == BlendFactor.SOURCE_ALPHA:
        return FVector4(source_color.a)
    elif factor == BlendFactor.ONE_MINUS_SOURCE_ALPHA:
        return FVector4(1 - source_color.a)
    elif factor == BlendFactor.DESTINATION_ALPHA:
        return FVector4(destination_color.a)
    elif factor == BlendFactor.ONE_MINUS_DESTINATION_ALPHA:
        return FVector4(1 - destination_color.a)
    elif factor == BlendFactor.BLEND_COLOR:
        return blend_color
    elif factor == BlendFactor.ONE_MINUS_BLEND_COLOR:
        return 1 - blend_color
    elif factor == BlendFactor.BLEND_ALPHA:
        return blend_color.a
    elif factor == BlendFactor.ONE_MINUS_BLEND_ALPHA:
        return FVector4(1 - blend_color.a)
    assert False


@pytest.mark.parametrize("blend_source", BlendFactor)
@pytest.mark.parametrize("blend_destination", BlendFactor)
def test_source_destination_factors(
    blend_source,
    blend_destination,
    render_target,
) -> None:
    color = FVector4(0.45, 0.3, 0.8, 0.333)
    clear_color = FVector4(0.2, 0.5, 0.2, 1)
    blend_color = FVector4(0.8, 0.7, 0.6, 0.5)

    clear_render_target(render_target, color=clear_color.rgb)

    shader = Shader(vertex=BytesIO(VERTEX_SHADER), fragment=BytesIO(FRAGMENT_SHADER))

    draw_fullscreen_quad(
        render_target,
        shader,
        color,
        blend_source,
        blend_destination,
        None,
        None,
        BlendFunction.ADD,
        blend_color,
    )

    source_factor = calculate_factor(blend_source, color, clear_color, blend_color)
    destination_factor = calculate_factor(blend_destination, color, clear_color, blend_color)
    expected_color = ((color * source_factor) + (clear_color * destination_factor)).clamp(0.0, 1.0)
    if isinstance(render_target, Window):
        expected_color = expected_color.rgbl

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0), render_target.size)
    )
    assert all(
        c.r == pytest.approx(expected_color[0], abs=0.01)
        and c.g == pytest.approx(expected_color[1], abs=0.01)
        and c.b == pytest.approx(expected_color[2], abs=0.01)
        and c.a == pytest.approx(expected_color[3], abs=0.01)
        for c in colors
    )


@pytest.mark.parametrize("blend_source", BlendFactor)
@pytest.mark.parametrize("blend_destination", BlendFactor)
def test_source_destination_alpha_factors(
    render_target,
    blend_source,
    blend_destination,
):
    color = FVector4(0.45, 0.3, 0.8, 0.333)
    clear_color = FVector4(0.2, 0.5, 0.2, 1)
    blend_color = FVector4(0.8, 0.7, 0.6, 0.5)

    clear_render_target(render_target, color=clear_color.rgb)

    shader = Shader(vertex=BytesIO(VERTEX_SHADER), fragment=BytesIO(FRAGMENT_SHADER))

    draw_fullscreen_quad(
        render_target,
        shader,
        color,
        BlendFactor.ONE,
        BlendFactor.ONE,
        blend_source,
        blend_destination,
        BlendFunction.ADD,
        blend_color,
    )

    source_factor = calculate_factor(blend_source, color, clear_color, blend_color)
    destination_factor = calculate_factor(blend_destination, color, clear_color, blend_color)
    expected_color = (
        FVector4(color.r, color.g, color.b, color.a * source_factor[3])
        + FVector4(
            clear_color.r, clear_color.g, clear_color.b, clear_color.a * destination_factor[3]
        )
    ).clamp(0.0, 1.0)
    if isinstance(render_target, Window):
        expected_color = expected_color.rgbl

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0), render_target.size)
    )
    assert all(
        c.r == pytest.approx(expected_color[0], abs=0.01)
        and c.g == pytest.approx(expected_color[1], abs=0.01)
        and c.b == pytest.approx(expected_color[2], abs=0.01)
        and c.a == pytest.approx(expected_color[3], abs=0.01)
        for c in colors
    )


@pytest.mark.parametrize("blend_function", BlendFunction)
def test_function(render_target, blend_function):
    color = FVector4(0.45, 0.3, 0.8, 0.333)
    clear_color = FVector4(0.2, 0.5, 0.2, 1)

    clear_render_target(render_target, color=clear_color.rgb)

    shader = Shader(vertex=BytesIO(VERTEX_SHADER), fragment=BytesIO(FRAGMENT_SHADER))

    draw_fullscreen_quad(
        render_target,
        shader,
        color,
        BlendFactor.ONE,
        BlendFactor.ONE,
        None,
        None,
        blend_function,
        None,
    )

    source = color
    destination = clear_color
    if blend_function == BlendFunction.ADD:
        expected_color = source + destination
    elif blend_function == BlendFunction.SUBTRACT:
        expected_color = source - destination
    elif blend_function == BlendFunction.SUBTRACT_REVERSED:
        expected_color = destination - source
    elif blend_function == BlendFunction.MIN:
        expected_color = FVector4(*(min(s, d) for s, d in zip(source, destination)))
    elif blend_function == BlendFunction.MAX:
        expected_color = FVector4(*(max(s, d) for s, d in zip(source, destination)))
    expected_color = expected_color.clamp(0.0, 1.0)
    if isinstance(render_target, Window):
        expected_color = expected_color.rgbl

    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0), render_target.size)
    )
    assert all(
        c.r == pytest.approx(expected_color[0], abs=0.01)
        and c.g == pytest.approx(expected_color[1], abs=0.01)
        and c.b == pytest.approx(expected_color[2], abs=0.01)
        and c.a == pytest.approx(expected_color[3], abs=0.01)
        for c in colors
    )


def test_default_blend_color(render_target):
    clear_render_target(render_target, color=FVector3(0, 0, 0))

    shader = Shader(vertex=BytesIO(VERTEX_SHADER), fragment=BytesIO(FRAGMENT_SHADER))

    draw_fullscreen_quad(
        render_target,
        shader,
        FVector4(0.5, 0.5, 0.5, 1),
        BlendFactor.BLEND_COLOR,
        BlendFactor.ZERO,
        None,
        None,
        BlendFunction.ADD,
        None,
    )
    expected_color = FVector4(0.5, 0.5, 0.5, 1)
    colors = read_color_from_render_target(
        render_target, IRectangle(IVector2(0), render_target.size)
    )
    assert all(
        c.r == pytest.approx(expected_color[0], abs=0.01)
        and c.g == pytest.approx(expected_color[1], abs=0.01)
        and c.b == pytest.approx(expected_color[2], abs=0.01)
        and c.a == pytest.approx(expected_color[3], abs=0.01)
        for c in colors
    )
