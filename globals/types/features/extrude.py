from typing import TypedDict

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