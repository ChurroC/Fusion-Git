from typing import Literal, TypedDict
from ..utils import Error, Point3D

class CircleCurve(TypedDict):
    type: Literal["adsk::fusion::SketchCircle"]
    center_point: Point3D
    radius: str
class LineCurve(TypedDict):
    type: Literal["adsk::fusion::SketchLine"]
    start_point: Point3D
    end_point: Point3D
Curve = LineCurve | CircleCurve

class PlaneFace(TypedDict):
    type: Literal["face"]
class PlaneCustom(TypedDict):
    type: Literal["custom_plane"]
    index: int
class PlaneBase(TypedDict):
    type: Literal["base_plane"]
    name: int
Plane = PlaneFace | PlaneCustom | PlaneBase

class SketchDetails(TypedDict):
    curves: list[Curve | Error]
    plane: Plane | Error

class SketchFeature(TypedDict):
    name: str
    type: Literal["adsk::fusion::Sketch"]
    index: int
    details: SketchDetails | Error