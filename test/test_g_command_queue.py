import pytest

from egraphics import ComputeGCommandQueue
from egraphics import GCommandQueue
from egraphics import GeneralGCommandQueue
from egraphics import GraphicsGCommandQueue
from egraphics import PresentationGCommandQueue
from egraphics import TransferGCommandQueue
from egraphics import use_vulkan

BASIC_COMMAND_QUEUE_CLS = (
    GCommandQueue,
    GraphicsGCommandQueue,
    PresentationGCommandQueue,
    ComputeGCommandQueue,
    TransferGCommandQueue,
    GeneralGCommandQueue,
)
ODD_COMMAND_QUEUE_CLS = (
    type(
        "GraphicsPresentationGCommandQueue", (GraphicsGCommandQueue, PresentationGCommandQueue), {}
    ),
    type(
        "ComputePresentationGCommandQueue", (ComputeGCommandQueue, PresentationGCommandQueue), {}
    ),
    type(
        "TransferPresentationGCommandQueue", (TransferGCommandQueue, PresentationGCommandQueue), {}
    ),
)
COMMAND_QUEUE_CLS = (*BASIC_COMMAND_QUEUE_CLS, *ODD_COMMAND_QUEUE_CLS)


@pytest.mark.parametrize("cls", COMMAND_QUEUE_CLS)
def test_initialize_no_vulkan_instance(no_vulkan, cls):
    with pytest.raises(RuntimeError) as excinfo:
        cls()
    assert str(excinfo.value) == f"no available queue with requested capabilities"


@pytest.mark.parametrize("cls", COMMAND_QUEUE_CLS)
def test_initialize(vulkan, cls):
    cls()


@pytest.mark.parametrize("cls", COMMAND_QUEUE_CLS)
def test_close(vulkan, cls):
    g_command_queue = cls()
    assert g_command_queue.is_open
    g_command_queue.close()
    assert not g_command_queue.is_open


@pytest.mark.parametrize("cls", COMMAND_QUEUE_CLS)
def test_context_manager(vulkan, cls):
    with cls() as g_command_queue:
        assert g_command_queue.is_open
    assert not g_command_queue.is_open


@pytest.mark.parametrize("cls", COMMAND_QUEUE_CLS)
def test_close_with_vulkan(no_vulkan, cls, window):
    with use_vulkan(window.vk_instance, window.vk_surface):
        g_command_queue = cls()
        assert g_command_queue.is_open
    assert not g_command_queue.is_open
