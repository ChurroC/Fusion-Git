from typing import Literal, TypedDict
from ..timeline import Error

class Point3D(TypedDict):
    x: str
    y: str
    z: str
class CircleCurve(TypedDict):
    type: Literal["adsk::fusion::SketchCircle"]
    centerPoint: Point3D
    radius: str
class LineCurve(TypedDict):
    type: Literal["adsk::fusion::SketchLine"]
    startPoint: Point3D
    endPoint: Point3D

class PlaneFace(TypedDict):
    type: Literal["face"]
class PlaneCustom(TypedDict):
    type: Literal["custom_plane"]
    index: int
class PlaneBase(TypedDict):
    type: Literal["base_plane"]
    name: int

class SketchDetails(TypedDict, total=False):
    curves: list[LineCurve | CircleCurve]
    plane: PlaneFace | PlaneCustom | PlaneBase

class SketchFeature(TypedDict):
    name: str
    type: Literal["adsk::fusion::Sketch"]
    index: int
    details: SketchDetails | Error