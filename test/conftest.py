# doorlord
# egraphics
from . import resources

# egraphics
from egraphics import clear_render_target
from egraphics._render_target import WindowRenderTargetMixin
from egraphics._state import get_gl_version
from egraphics._state import reset_state

# emath
from emath import FVector3
from emath import IVector2

# eplatform
from eplatform import EventLoop
from eplatform import Platform
from eplatform import Window
from eplatform import get_window

# pytest
import pytest

# python
import asyncio
import gc
from math import isclose
from pathlib import Path


class TestWindow(Window, WindowRenderTargetMixin):
    pass


@pytest.fixture(autouse=True)
def _reset_state():
    yield
    reset_state()
    gc.collect()


@pytest.fixture(scope="session")
def platform():
    with Platform(window_cls=TestWindow):
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


@pytest.fixture
def render_target(window, capture_event):
    if window.size != IVector2(10, 10):

        def _():
            window.resize(IVector2(10, 10))

        capture_event(_, window.resized)
    clear_render_target(window, depth=1, color=FVector3(0))
    return window


@pytest.fixture
def resource_dir():
    return Path(resources.__file__).parent
