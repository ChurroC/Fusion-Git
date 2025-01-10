from __future__ import annotations  # Postpones evaluation of annotations

from typing import Literal, NotRequired, TypedDict

from .features.sketch_type import SketchFeature
from .features.extrude_type import ExtrudeFeature
from .features.component_type import ComponentFeature
from .utils_type import Error, ReadableValue

Feature = SketchFeature | ExtrudeFeature | ComponentFeature


class ComponentReferences(TypedDict):
    name: str
    path: str


class ComponentInfo(TypedDict):
    path: str
    is_linked: bool
    name: str
    units: NotRequired[ReadableValue[Literal[0, 1, 2, 3, 4]]]
    feature_index: list[int]
    references: list[ComponentReferences]
    assembly: NotRequired[Data]


class Data(TypedDict):
    timeline: list[Feature | Error]
    components: dict[str, ComponentInfo]
