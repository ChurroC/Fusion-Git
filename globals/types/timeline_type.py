from typing import TypedDict
from .features.sketch_type import SketchFeature
from .features.extrude_type import ExtrudeFeature
from .utils_type import Error

Feature = SketchFeature | ExtrudeFeature

class Timeline(TypedDict):
    document_name: str
    units: int
    features: list[Feature | Error]