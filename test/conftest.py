# egraphics
from egraphics import reset_state

# eplatform
from eplatform import Platform

# pytest
import pytest

Platform.register_deactivate_callback(reset_state)


@pytest.fixture
def platform():
    with Platform():
        yield
