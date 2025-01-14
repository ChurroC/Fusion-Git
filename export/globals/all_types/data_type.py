from __future__ import annotations  # Postpones evaluation of annotations

from typing import Literal, NotRequired, TypedDict

from .features.sketch_type import SketchFeature
from .features.extrude_type import ExtrudeFeature
from .features.component_type import ComponentFeature
from .utils_type import Error, NoMarkdown, ReadableValue

Feature = SketchFeature | ExtrudeFeature | ComponentFeature


# Later I could add a info tab
class ComponentReferences(TypedDict):
    path: str
    name: str
    link_to_component: str
    link_to_reference: str


class ComponentInfo(TypedDict):
    index: int
    path: str
    name: str
    is_linked: bool
    units: NotRequired[ReadableValue[Literal[0, 1, 2, 3, 4]]]
    features: list[Feature | Error]
    references: list[ComponentReferences]
    assembly: NotRequired[NoMarkdown[Data]]


class Data(TypedDict):
    timeline: list[Feature | Error]
    components: dict[str, ComponentInfo]
