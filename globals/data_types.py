from typing import TypedDict

class Curves(TypedDict):
    type: str
    data: list[list[float]]

class Plane(TypedDict):
    objectType: str
    name: str

class Sketch(TypedDict):
    curves: Curves
    plane: Plane

class ExtrudeFeature(TypedDict):
    name: str
    extrudeType: str
    operation: str
    start: float
    end: float
    distance: float
    taperAngle: float
    taperType: str
    isSymmetric: bool
    isDirectionFlipped: bool
    isSolid: bool
    isNonAssociative: bool

class Feature(TypedDict):
    name: str
    type: str
    index: int
    details: Sketch | ExtrudeFeature

class Timeline(TypedDict):
    documentName: str
    units: int
    features: list[Feature]
