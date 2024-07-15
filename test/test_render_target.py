# egraphics
from egraphics import clear_render_target
from egraphics import read_color_from_render_target
from egraphics import read_depth_from_render_target
from egraphics import set_read_render_target
import egraphics._render_target

# egeometry
from egeometry import IRectangle

# emath
from emath import FVector3
from emath import FVector4
from emath import IVector2

# eplatform
from eplatform import Platform

# pyopengl
from OpenGL.GL import GL_READ_FRAMEBUFFER_BINDING
from OpenGL.GL import glGetIntegerv


def test_default_state():
    assert egraphics._render_target._read_render_target is None


def test_reset_state():
    egraphics._render_target._read_render_target = 2

    with Platform():
        pass

    assert egraphics._render_target._read_render_target is None


def test_set_read_window(platform, window):
    set_read_render_target(window)
    assert egraphics._render_target._read_render_target is window
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == 0

    set_read_render_target(window)
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == 0


def test_clear_window(window, is_close):
    rect = IRectangle(IVector2(0, 0), window.size)

    clear_render_target(window, color=FVector3(0.3, 0.5, 0.7), depth=1)
    print(list(read_color_from_render_target(window, rect)))
    assert all(
        is_close(p, FVector4(0.3, 0.5, 0.7, 1))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(is_close(p, 1) for p in read_depth_from_render_target(window, rect))

    clear_render_target(window, color=FVector3(0.2, 0.4, 0.6))
    assert all(
        is_close(p, FVector4(0.2, 0.4, 0.6, 1))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(p == 1 for p in read_depth_from_render_target(window, rect))

    clear_render_target(window, depth=0.5)
    assert all(
        is_close(p, FVector4(0.2, 0.4, 0.6, 1))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(is_close(p, 0.5) for p in read_depth_from_render_target(window, rect))
