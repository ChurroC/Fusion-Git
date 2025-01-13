from __future__ import annotations  # Postpones evaluation of annotations

from typing import Literal, NotRequired, TypedDict

from .features.sketch_type import SketchFeature
from .features.extrude_type import ExtrudeFeature
from .features.component_type import ComponentFeature
from .utils_type import Error, NoMarkdown, ReadableValue

Feature = SketchFeature | ExtrudeFeature | ComponentFeature


class ComponentReferences(TypedDict):
    name: str
    path: str


class ComponentInfo(TypedDict):
    path: str
    is_linked: bool
    name: str
    units: NotRequired[ReadableValue[Literal[0, 1, 2, 3, 4]]]
    features: list[Feature | Error]
    references: list[ComponentReferences]
    assembly: NotRequired[NoMarkdown[Data]]


Timeline = list[Feature | Error]


class Data(TypedDict):
    timeline: Timeline
    components: dict[str, ComponentInfo]
