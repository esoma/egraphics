# egraphics
from egraphics import clear_render_target
from egraphics import read_color_from_render_target
from egraphics import read_depth_from_render_target
from egraphics import reset_state
import egraphics._render_target
from egraphics._render_target import set_draw_render_target
from egraphics._render_target import set_read_render_target

# egeometry
from egeometry import IRectangle

# emath
from emath import FVector3
from emath import IVector2

# pyopengl
from OpenGL.GL import GL_DRAW_FRAMEBUFFER_BINDING
from OpenGL.GL import GL_READ_FRAMEBUFFER_BINDING
from OpenGL.GL import GL_VIEWPORT
from OpenGL.GL import glGetIntegerv


def test_default_state():
    assert egraphics._render_target._draw_render_target is None
    assert egraphics._render_target._draw_render_target_size is None
    assert egraphics._render_target._read_render_target is None


def test_reset_state():
    egraphics._render_target._draw_render_target = 1
    egraphics._render_target._draw_render_target = 3
    egraphics._render_target._read_render_target = 2

    reset_state()

    assert egraphics._render_target._draw_render_target is None
    assert egraphics._render_target._draw_render_target_size is None
    assert egraphics._render_target._read_render_target is None


def test_set_draw_window(platform, window):
    set_draw_render_target(window)
    assert egraphics._render_target._draw_render_target is window
    assert egraphics._render_target._draw_render_target_size == window.size
    assert glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING) == 0
    assert glGetIntegerv(GL_VIEWPORT)[0] == 0
    assert glGetIntegerv(GL_VIEWPORT)[1] == 0
    assert glGetIntegerv(GL_VIEWPORT)[2] == window.size.x
    assert glGetIntegerv(GL_VIEWPORT)[3] == window.size.y

    set_draw_render_target(window)
    assert egraphics._render_target._draw_render_target is window
    assert egraphics._render_target._draw_render_target_size == window.size
    assert glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING) == 0
    assert glGetIntegerv(GL_VIEWPORT)[0] == 0
    assert glGetIntegerv(GL_VIEWPORT)[1] == 0
    assert glGetIntegerv(GL_VIEWPORT)[2] == window.size.x
    assert glGetIntegerv(GL_VIEWPORT)[3] == window.size.y

    window.size = IVector2(201, 102)
    set_draw_render_target(window)
    assert egraphics._render_target._draw_render_target is window
    assert egraphics._render_target._draw_render_target_size == window.size
    assert glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING) == 0
    assert glGetIntegerv(GL_VIEWPORT)[0] == 0
    assert glGetIntegerv(GL_VIEWPORT)[1] == 0
    assert glGetIntegerv(GL_VIEWPORT)[2] == window.size.x
    assert glGetIntegerv(GL_VIEWPORT)[3] == window.size.y


def test_set_read_window(platform, window):
    set_read_render_target(window)
    assert egraphics._render_target._read_render_target is window
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == 0

    set_read_render_target(window)
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == 0


def test_clear_window(window, is_kinda_close):
    rect = IRectangle(IVector2(0, 0), window.size)

    clear_render_target(window, color=FVector3(0.3, 0.5, 0.7), depth=1)
    assert all(
        is_kinda_close(p.rgb, FVector3(0.3, 0.5, 0.7))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(is_kinda_close(p, 1) for p in read_depth_from_render_target(window, rect))

    clear_render_target(window, color=FVector3(0.2, 0.4, 0.6))
    assert all(
        is_kinda_close(p.rgb, FVector3(0.2, 0.4, 0.6))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(is_kinda_close(p, 1) for p in read_depth_from_render_target(window, rect))

    clear_render_target(window, depth=0.5)
    assert all(
        is_kinda_close(p.rgb, FVector3(0.2, 0.4, 0.6))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(is_kinda_close(p, 0.5) for p in read_depth_from_render_target(window, rect))
