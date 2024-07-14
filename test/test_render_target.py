# egraphics
from egraphics import clear_render_target
from egraphics import read_color_from_render_target
from egraphics import read_depth_from_render_target
from egraphics import set_read_render_target
import egraphics._render_target

# egeometry
from egeometry import IRectangle

# emath
from emath import FArray
from emath import FVector3
from emath import FVector4
from emath import FVector4Array
from emath import IVector2

# eplatform
from eplatform import Platform

# pyopengl
from OpenGL.GL import GL_COLOR_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_READ_FRAMEBUFFER_BINDING
from OpenGL.GL import glGetIntegerv

# pytest
import pytest

# python
from unittest.mock import patch


def test_default_state():
    assert egraphics._render_target._read_render_target is None
    assert egraphics._render_target._clear_color is None
    assert egraphics._render_target._clear_depth is None


def test_reset_state():
    egraphics._render_target._read_render_target = 2
    egraphics._render_target._clear_color = 3
    egraphics._render_target._clear_depth = 4

    with Platform():
        pass

    assert egraphics._render_target._read_render_target is None
    assert egraphics._render_target._clear_color is None
    assert egraphics._render_target._clear_depth is None


def test_set_read_window(platform, window):
    set_read_render_target(window)
    assert egraphics._render_target._read_render_target is window
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == 0

    set_read_render_target(window)
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == 0


@pytest.mark.parametrize("size", [IVector2(1, 1), IVector2(2, 2)])
def test_read_color_from_window(window, size):
    colors = read_color_from_render_target(window, IRectangle(IVector2(0, 0), size))
    assert isinstance(colors, FVector4Array)
    assert colors == FVector4Array(*[FVector4(0, 0, 0, 1)] * size.x * size.y)


@pytest.mark.parametrize("size", [IVector2(1, 1), IVector2(2, 2)])
def test_read_depth_from_window(window, size):
    colors = read_depth_from_render_target(window, IRectangle(IVector2(0, 0), size))
    assert isinstance(colors, FArray)
    assert colors == FArray(*[-1] * size.x * size.y)


@patch("egraphics._render_target.set_draw_render_target")
@patch("egraphics._render_target.glClear")
def test_clear_render_target_defaults(glClear, set_draw_render_target, platform):
    clear_render_target(None)
    glClear.assert_not_called()
    set_draw_render_target.assert_not_called()


@patch("egraphics._render_target.set_draw_render_target")
@patch("egraphics._render_target.glClear")
@patch("egraphics._render_target.glClearColor")
@patch("egraphics._render_target.glClearDepthf")
@pytest.mark.parametrize("color", [None, FVector3(1, 2, 3), FVector3(0)])
@pytest.mark.parametrize("depth, expected_depth", [(None, None), (1, 1), (0, 0.5), (-1, 0)])
def test_clear_render_target(
    glClearDepthf,
    glClearColor,
    glClear,
    set_draw_render_target,
    platform,
    color,
    depth,
    expected_depth,
):
    target = object()

    mask = 0
    if color is not None:
        mask |= GL_COLOR_BUFFER_BIT
    if depth is not None:
        mask |= GL_DEPTH_BUFFER_BIT

    clear_render_target(target, color=color, depth=depth)

    if color is not None:
        glClearColor.assert_called_once_with(*color, 1.0)
    assert egraphics._render_target._clear_color == color

    if depth is not None:
        glClearDepthf.assert_called_once_with(expected_depth)
    assert egraphics._render_target._clear_depth == depth

    if mask == 0:
        set_draw_render_target.assert_not_called()
        glClear.assert_not_called()
    else:
        set_draw_render_target.assert_called_once_with(target)
        glClear.assert_called_once_with(mask)

    glClearColor.reset_mock()
    glClearDepthf.reset_mock()
    glClear.reset_mock()
    set_draw_render_target.reset_mock()

    clear_render_target(target, color=color, depth=depth)

    glClearColor.assert_not_called()
    glClearDepthf.assert_not_called()

    if mask == 0:
        set_draw_render_target.assert_not_called()
        glClear.assert_not_called()
    else:
        set_draw_render_target.assert_called_once_with(target)
        glClear.assert_called_once_with(mask)

    glClear.reset_mock()
    set_draw_render_target.reset_mock()

    clear_render_target(target)

    glClearColor.assert_not_called()
    glClearDepthf.assert_not_called()
    set_draw_render_target.assert_not_called()
    glClear.assert_not_called()


def test_clear_window(window, is_close):
    clear_render_target(window)
    rect = IRectangle(IVector2(0, 0), window.size)
    assert all(p == FVector4(0, 0, 0, 1) for p in read_color_from_render_target(window, rect))
    assert all(p == -1 for p in read_depth_from_render_target(window, rect))

    clear_render_target(window, color=FVector3(0.2, 0.4, 0.6))
    assert all(
        is_close(p, FVector4(0.2, 0.4, 0.6, 1))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(p == -1 for p in read_depth_from_render_target(window, rect))

    clear_render_target(window, depth=0.5)
    assert all(
        is_close(p, FVector4(0.2, 0.4, 0.6, 1))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(is_close(p, 0.5) for p in read_depth_from_render_target(window, rect))

    clear_render_target(window, color=FVector3(0.3, 0.5, 0.7), depth=1)
    assert all(
        is_close(p, FVector4(0.3, 0.5, 0.7, 1))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(is_close(p, 1) for p in read_depth_from_render_target(window, rect))
