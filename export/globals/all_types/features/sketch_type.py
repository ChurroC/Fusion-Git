from typing import Literal, TypedDict
from ..utils_type import Error, Point3D, ReadableValue


class CircleCurve(TypedDict):
    type: ReadableValue[Literal["adsk::fusion::SketchCircle"]]
    center_point: Point3D
    radius: str


class LineCurve(TypedDict):
    type: ReadableValue[Literal["adsk::fusion::SketchLine"]]
    start_point: Point3D
    end_point: Point3D


Curve = LineCurve | CircleCurve


class PlaneFace(TypedDict):
    type: ReadableValue[Literal["face"]]


class PlaneCustom(TypedDict):
    type: ReadableValue[Literal["custom_plane"]]
    index: int


class PlaneBase(TypedDict):
    type: ReadableValue[Literal["base_plane"]]
    name: str


Plane = PlaneFace | PlaneCustom | PlaneBase


class SketchDetails(TypedDict):
    curves: list[Curve | Error]
    plane: Plane | Error


class SketchFeature(TypedDict):
    index: int
    name: str
    type: ReadableValue[Literal["adsk::fusion::Sketch"]]
    details: SketchDetails | Error
