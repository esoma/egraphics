# egraphics
from egraphics._weak_fifo_set import WeakFifoSet

# pytest
import pytest


def test_weakness():
    class X:
        pass

    item = X()
    set = WeakFifoSet()

    set.add(item)
    assert set.pop() is item

    set.add(item)
    del item
    with pytest.raises(IndexError):
        set.pop()


def test_set_like():
    class X:
        pass

    x1 = X()
    x2 = X()
    set = WeakFifoSet()

    set.add(x1)
    set.add(x2)
    set.add(x1)

    assert set.pop() is x2
    assert set.pop() is x1
    with pytest.raises(IndexError):
        set.pop()


def test_remove():
    class X:
        pass

    items = [X(), X(), X()]
    set = WeakFifoSet()

    for item in items:
        set.add(item)

    set.remove(items[1])

    assert set.pop() is items[0]
    assert set.pop() is items[2]
    with pytest.raises(IndexError):
        set.pop()


def test_clear():
    class X:
        pass

    item = X()
    set = WeakFifoSet()

    set.add(item)
    set.clear()

    with pytest.raises(IndexError):
        set.pop()
