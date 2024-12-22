from typing import TypedDict
from .features.sketch import SketchFeature
from .features.extrude import ExtrudeFeature
from .utils import Error

class Timeline(TypedDict):
    document_name: str
    units: int
    features: list[SketchFeature | ExtrudeFeature | Error]