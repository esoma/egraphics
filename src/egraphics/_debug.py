__all__ = ["debug_callback"]

# egraphics
from ._egraphics import debug_gl

# python
from contextlib import contextmanager
from typing import Callable
from typing import Generator


@contextmanager
def debug_callback(f: Callable) -> Generator[None, None, None]:
    debug_gl(f)
    yield
