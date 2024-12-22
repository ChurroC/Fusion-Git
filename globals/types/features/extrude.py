from typing import Literal, TypedDict
from ..utils import Error, Point3D

# Extent Types
class SymmetricExtent(TypedDict):
    value: str  # "1 in"
    isFullLength: bool
class ExtentDistance(TypedDict):
    side_one: str | None  # "-2.00 in"
    side_two: str | None  # "1 in"
    symmetric: SymmetricExtent | None
class ExtrudeExtent(TypedDict):
    type: Literal[
        0,  # adsk.fusion.FeatureExtentTypes.OneSideFeatureExtentType
        1,  # adsk.fusion.FeatureExtentTypes.TwoSidesFeatureExtentType
        2   # adsk.fusion.FeatureExtentTypes.SymmetricFeatureExtentType
    ]  # OneSide=0, TwoSides=1, Symmetric=2
    distance: ExtentDistance
    
class OneSideExtent(TypedDict):
    type: Literal[0]
    distance: TypedDict("Position", {"x": int, "y": int, "z": int})

# Profile Types
class CircleProfile(TypedDict):
    type: Literal["circle"]
    center: Point3D
    radius: str
class LineProfile(TypedDict):
    type: Literal["line"]
    startPoint: Point3D
    endPoint: Point3D
class ProfileLoop(TypedDict):
    isOuter: bool
    vertices: list[CircleProfile | LineProfile]
class ProfileData(TypedDict):
    area: str  # "17.954 in"
    loops: list[ProfileLoop]
class SingleProfile(TypedDict):
    type: Literal["profile"]
    data: ProfileData
class PlanarFace(TypedDict):
    type: Literal["planar_face"]
    geometry: dict  # Could be more specific based on your needs

class ExtrudeDetails(TypedDict, total=False):
    operation: Literal[0, 1, 2, 3, 4, 5]  # Cut=0, Join=1, Intersect=2, NewBody=3, CutIntersect=4, CutJoin=5
    extent: ExtrudeExtent | Error
    profile: SingleProfile | PlanarFace | Error

class ExtrudeFeature(TypedDict):
    name: str
    type: Literal["adsk::fusion::ExtrudeFeature"]
    details: ExtrudeDetails | Error