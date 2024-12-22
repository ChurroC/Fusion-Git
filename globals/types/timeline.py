from typing import TypedDict
from .features.sketch import SketchFeature
from .features.extrude import ExtrudeFeature
from .utils import Error

class Timeline(TypedDict):
    documentName: str
    units: int
    features: list[SketchFeature | ExtrudeFeature | Error]
