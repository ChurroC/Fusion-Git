from typing import TypedDict
from .types import SketchFeature, ExtrudeFeature

class Timeline(TypedDict):
    documentName: str
    units: int
    features: list[SketchFeature | ExtrudeFeature]
