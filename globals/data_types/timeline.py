from typing import TypedDict

from globals.data_types.features.sketch import SketchFeature

class Timeline(TypedDict):
    documentName: str
    units: int
    features: list[SketchFeature]

class Error(TypedDict):
    error: str