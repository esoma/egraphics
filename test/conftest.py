# egraphics
from egraphics import clear_render_target
from egraphics._state import get_gl_version
from egraphics._state import reset_state

# emath
from emath import FVector3

# eplatform
from eplatform import Platform
from eplatform import get_window

# pytest
import pytest

# python
import gc
from math import isclose


@pytest.fixture(autouse=True)
def _reset_state():
    yield
    reset_state()
    gc.collect()


@pytest.fixture
def platform(_reset_state):
    with Platform():
        yield
    gc.collect()


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
def render_target(window):
    window.size = (10, 10)
    clear_render_target(window, depth=1, color=FVector3(0))
    return window
