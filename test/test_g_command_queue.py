import pytest

from egraphics import ComputeGCommand
from egraphics import GCommand
from egraphics import GCommandQueue
from egraphics import GeneralGCommand
from egraphics import GraphicsGCommand
from egraphics import PresentationGCommand
from egraphics import TransferGCommand
from egraphics import use_vulkan

BASIC_COMMAND_CLS = (
    GCommand,
    GraphicsGCommand,
    PresentationGCommand,
    ComputeGCommand,
    TransferGCommand,
    GeneralGCommand,
)
ODD_COMMAND_CLS = (
    type("GraphicsPresentationGCommand", (GraphicsGCommand, PresentationGCommand), {}),
    type("ComputePresentationGCommand", (ComputeGCommand, PresentationGCommand), {}),
    type("TransferPresentationGCommand", (TransferGCommand, PresentationGCommand), {}),
)
COMMAND_CLS = (*BASIC_COMMAND_CLS, *ODD_COMMAND_CLS)


@pytest.mark.parametrize("cls", COMMAND_CLS)
def test_initialize_no_vulkan_instance(no_vulkan, cls):
    with pytest.raises(RuntimeError) as excinfo:
        GCommandQueue(cls)
    assert str(excinfo.value) == f"no available queue with requested capabilities"


@pytest.mark.parametrize("cls", COMMAND_CLS)
def test_initialize(vulkan, cls):
    GCommandQueue(cls)


@pytest.mark.parametrize("cls", COMMAND_CLS)
def test_close(vulkan, cls):
    g_command_queue = GCommandQueue(cls)
    assert g_command_queue.is_open
    g_command_queue.close()
    assert not g_command_queue.is_open


@pytest.mark.parametrize("cls", COMMAND_CLS)
def test_context_manager(vulkan, cls):
    with GCommandQueue(cls) as g_command_queue:
        assert g_command_queue.is_open
    assert not g_command_queue.is_open


@pytest.mark.parametrize("cls", COMMAND_CLS)
def test_close_with_vulkan(no_vulkan, cls, window):
    with use_vulkan(window.vk_instance, window.vk_surface):
        g_command_queue = GCommandQueue(cls)
        assert g_command_queue.is_open
    assert not g_command_queue.is_open
