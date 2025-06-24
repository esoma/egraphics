import ctypes

import pytest
from egeometry import IRectangle
from emath import FVector3
from emath import FVector4
from emath import IVector2
from OpenGL.GL import GL_DRAW_FRAMEBUFFER_BINDING
from OpenGL.GL import GL_FRAMEBUFFER_COMPLETE
from OpenGL.GL import GL_READ_FRAMEBUFFER
from OpenGL.GL import GL_READ_FRAMEBUFFER_BINDING
from OpenGL.GL import GL_VIEWPORT
from OpenGL.GL import glCheckFramebufferStatus
from OpenGL.GL import glGetIntegerv

import egraphics._render_target
from egraphics import Image
from egraphics import Texture2d
from egraphics import TextureComponents
from egraphics import TextureRenderTarget
from egraphics import clear_render_target
from egraphics import read_color_from_render_target
from egraphics import read_depth_from_render_target
from egraphics import reset_state
from egraphics._render_target import set_draw_render_target
from egraphics._render_target import set_read_render_target


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


@pytest.mark.parametrize("depth", [False, True, None])
def test_texture_render_target(platform, resource_dir, depth):
    with open(resource_dir / "gamut.gif", "rb") as f:
        colors = Image(f).to_texture()
    if depth is None:
        depth = Texture2d(
            colors.size,
            TextureComponents.D,
            ctypes.c_float,
            b"\x00" * 4 * colors.size[0] * colors.size[1],
        )
    render_target = TextureRenderTarget([colors], depth=depth)
    assert render_target.size == IVector2(*colors.size)
    set_read_render_target(render_target)
    assert glCheckFramebufferStatus(GL_READ_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE


@pytest.mark.parametrize("depth", [False, True])
def test_set_draw_texture(platform, resource_dir, depth):
    with open(resource_dir / "gamut.gif", "rb") as f:
        colors = Image(f).to_texture()
    render_target = TextureRenderTarget([colors], depth=depth)

    set_draw_render_target(render_target)
    assert egraphics._render_target._draw_render_target is render_target
    assert egraphics._render_target._draw_render_target_size == render_target.size
    assert glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING) == render_target._gl_framebuffer
    assert glGetIntegerv(GL_VIEWPORT)[0] == 0
    assert glGetIntegerv(GL_VIEWPORT)[1] == 0
    assert glGetIntegerv(GL_VIEWPORT)[2] == render_target.size.x
    assert glGetIntegerv(GL_VIEWPORT)[3] == render_target.size.y

    set_draw_render_target(render_target)
    assert egraphics._render_target._draw_render_target is render_target
    assert egraphics._render_target._draw_render_target_size == render_target.size
    assert glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING) == render_target._gl_framebuffer
    assert glGetIntegerv(GL_VIEWPORT)[0] == 0
    assert glGetIntegerv(GL_VIEWPORT)[1] == 0
    assert glGetIntegerv(GL_VIEWPORT)[2] == render_target.size.x
    assert glGetIntegerv(GL_VIEWPORT)[3] == render_target.size.y


def test_set_draw_window(platform, window, capture_event):
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

    def _():
        window.resize(IVector2(201, 102))

    capture_event(_, window.resized)

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
    assert egraphics._render_target._read_render_target is window
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == 0


@pytest.mark.parametrize("depth", [False, True])
def test_set_read_texture(platform, resource_dir, depth):
    with open(resource_dir / "gamut.gif", "rb") as f:
        colors = Image(f).to_texture()
    render_target = TextureRenderTarget([colors], depth=depth)

    set_read_render_target(render_target)
    assert egraphics._render_target._read_render_target is render_target
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == render_target._gl_framebuffer

    set_read_render_target(render_target)
    assert egraphics._render_target._read_render_target is render_target
    assert glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == render_target._gl_framebuffer


def test_clear_window(window, is_kinda_close, capture_event):
    def _():
        window.resize(IVector2(10, 10))

    capture_event(_, window.resized)

    rect = IRectangle(IVector2(0, 0), window.size)

    clear_render_target(window, color=FVector4(0.3, 0.5, 0.7, 1.0), depth=1)
    assert all(
        is_kinda_close(p.rgb, FVector3(0.3, 0.5, 0.7))
        for p in read_color_from_render_target(window, rect)
    )
    assert all(is_kinda_close(p, 1) for p in read_depth_from_render_target(window, rect))

    clear_render_target(window, color=FVector4(0.2, 0.4, 0.6, 0.8))
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


@pytest.mark.parametrize("depth", [False, True, None])
def test_clear_render_target(platform, is_kinda_close, resource_dir, depth):
    with open(resource_dir / "gamut.gif", "rb") as f:
        colors_1 = Image(f).to_texture()
    with open(resource_dir / "gamut.gif", "rb") as f:
        colors_2 = Image(f).to_texture()
    colors_3 = Texture2d(
        colors_1.size,
        TextureComponents.RGBA,
        ctypes.c_float,
        b"\x00" * 4 * colors_1.size[0] * colors_1.size[1] * 4,
    )
    if depth is None:
        depth = Texture2d(
            colors_1.size,
            TextureComponents.D,
            ctypes.c_float,
            b"\x00" * 4 * colors_1.size[0] * colors_1.size[1],
        )
    render_target = TextureRenderTarget([colors_1, colors_2, colors_3], depth=depth)

    rect = IRectangle(IVector2(0, 0), render_target.size)

    clear_render_target(render_target, color=FVector4(0.3, 0.5, 0.7, 0.5), depth=1)
    assert all(
        is_kinda_close(p.rgb, FVector3(0.3, 0.5, 0.7))
        for p in read_color_from_render_target(render_target, rect)
    )
    assert all(
        is_kinda_close(p.rgb, FVector3(0.3, 0.5, 0.7))
        for p in read_color_from_render_target(render_target, rect, index=1)
    )
    assert all(
        is_kinda_close(p, FVector4(0.3, 0.5, 0.7, 0.5))
        for p in read_color_from_render_target(render_target, rect, index=2)
    )
    if depth is not False:
        assert all(
            is_kinda_close(p, 1) for p in read_depth_from_render_target(render_target, rect)
        )

    clear_render_target(render_target, color=FVector4(0.2, 0.4, 0.6, 0.8))
    assert all(
        is_kinda_close(p.rgb, FVector3(0.2, 0.4, 0.6))
        for p in read_color_from_render_target(render_target, rect)
    )
    assert all(
        is_kinda_close(p.rgb, FVector3(0.2, 0.4, 0.6))
        for p in read_color_from_render_target(render_target, rect, index=1)
    )
    assert all(
        is_kinda_close(p, FVector4(0.2, 0.4, 0.6, 0.8))
        for p in read_color_from_render_target(render_target, rect, index=2)
    )
    if depth is not False:
        assert all(
            is_kinda_close(p, 1) for p in read_depth_from_render_target(render_target, rect)
        )

    clear_render_target(render_target, depth=0.5)
    assert all(
        is_kinda_close(p.rgb, FVector3(0.2, 0.4, 0.6))
        for p in read_color_from_render_target(render_target, rect)
    )
    assert all(
        is_kinda_close(p.rgb, FVector3(0.2, 0.4, 0.6))
        for p in read_color_from_render_target(render_target, rect, index=1)
    )
    assert all(
        is_kinda_close(p, FVector4(0.2, 0.4, 0.6, 0.8))
        for p in read_color_from_render_target(render_target, rect, index=2)
    )
    if depth is not False:
        assert all(
            is_kinda_close(p, 0.5) for p in read_depth_from_render_target(render_target, rect)
        )
