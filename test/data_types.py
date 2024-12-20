from typing import TypedDict

class Feature(TypedDict):
    name: str
    type: str
    index: int

class Timeline(TypedDict):
    documentName: str
    units: int
    features: list[Feature]
