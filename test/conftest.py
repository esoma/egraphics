import os

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(os.getcwd() + "/vendor/SDL")

import asyncio
import gc
from ctypes import c_float
from ctypes import c_uint8
from math import isclose
from pathlib import Path

import pytest
from emath import FVector4
from emath import IVector2
from emath import UVector2
from eplatform import EventLoop
from eplatform import Platform
from eplatform import Window
from eplatform import get_window

from egraphics import clear_render_target
from egraphics._debug import debug_callback
from egraphics._render_target import TextureRenderTarget
from egraphics._render_target import WindowRenderTargetMixin
from egraphics._state import get_gl_version
from egraphics._state import reset_state
from egraphics._texture_2d import Texture2d
from egraphics._texture_2d import TextureComponents

from . import resources


class TestWindow(Window, WindowRenderTargetMixin):
    pass


@pytest.fixture(autouse=True)
def _reset_state():
    yield
    reset_state()
    gc.collect()


@pytest.fixture(scope="session")
def platform():
    with Platform(window_cls=TestWindow), debug_callback(print):
        yield
    gc.collect()


@pytest.fixture
def capture_event():
    def _(f, e):
        event = None

        async def test():
            nonlocal event
            f()
            event = await asyncio.wait_for(e, timeout=1)

        loop = EventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(test())

        return event

    return _


@pytest.fixture
def window(platform):
    return get_window()


@pytest.fixture
def gl_version(platform):
    return get_gl_version()


@pytest.fixture
def is_close():
    def _(a, b, rel_tol=0.01):
        try:
            for l, r in zip(a, b):
                if not isclose(l, r, rel_tol=rel_tol):
                    return False
            return True
        except TypeError:
            pass
        return isclose(a, b, rel_tol=rel_tol)

    return _


@pytest.fixture
def is_kinda_close():
    def _(a, b, abs_tol=0.09):
        try:
            for l, r in zip(a, b):
                if not isclose(l, r, abs_tol=abs_tol):
                    return False
            return True
        except TypeError:
            pass
        return isclose(a, b, abs_tol=abs_tol)

    return _


@pytest.fixture(params=["window", "texture", "texture_with_depth_texture"])
def render_target(platform, capture_event, request):
    if request.param == "window":
        render_target = request.getfixturevalue("window")
        if render_target.size != IVector2(10, 10):

            def _():
                render_target.resize(IVector2(10, 10))

            capture_event(_, render_target.resized)
        clear_render_target(render_target, depth=1, color=FVector4(0, 0, 0, 1))
    elif request.param == "texture":
        render_target = TextureRenderTarget(
            [Texture2d(UVector2(10), TextureComponents.RGBA, c_uint8, b"\x00" * (10 * 10 * 4))],
            depth=True,
        )
    elif request.param == "texture_with_depth_texture":
        render_target = TextureRenderTarget(
            [Texture2d(UVector2(10), TextureComponents.RGBA, c_uint8, b"\x00" * (10 * 10 * 4))],
            depth=Texture2d(UVector2(10), TextureComponents.D, c_float, b"\x00" * (4 * 10 * 10)),
        )
    return render_target


@pytest.fixture
def resource_dir():
    return Path(resources.__file__).parent
