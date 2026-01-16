__all__ = [
    "GCommand",
    "GCommandRequirements",
    "TransferGCommand",
    "ComputeGCommand",
    "GraphicsGCommand",
    "PresentationGCommand",
    "GeneralGCommand",
]

from typing import ClassVar
from typing import NamedTuple


class GCommand:
    _egraphics__requires_transfer: ClassVar[bool] = False
    _egraphics__requires_compute: ClassVar[bool] = False
    _egraphics__requires_graphics: ClassVar[bool] = False
    _egraphics__requires_presentation: ClassVar[bool] = False


class TransferGCommand(GCommand):
    _egraphics__requires_transfer: ClassVar[bool] = True


class ComputeGCommand(TransferGCommand):
    _egraphics__requires_compute: ClassVar[bool] = True


class GraphicsGCommand(TransferGCommand):
    _egraphics__requires_graphics: ClassVar[bool] = True


class PresentationGCommand(GCommand):
    _egraphics__requires_presentation: ClassVar[bool] = True


class GeneralGCommand(ComputeGCommand, GraphicsGCommand, PresentationGCommand):
    pass


class GCommandRequirements(NamedTuple):
    transfer: bool
    compute: bool
    graphics: bool
    presentation: bool


def get_g_command_requirements(cls: type[GCommand]) -> GCommandRequirements:
    return GCommandRequirements(
        cls._egraphics__requires_transfer,
        cls._egraphics__requires_compute,
        cls._egraphics__requires_graphics,
        cls._egraphics__requires_presentation,
    )
