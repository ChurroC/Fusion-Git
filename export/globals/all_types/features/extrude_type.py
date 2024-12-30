from typing import Literal, TypedDict
from ..utils_type import Error, ReadableValue


class OneSideExtent(TypedDict):
    type: ReadableValue[Literal[0]]
    side_one: str  # "-2.00 in"


class TwoSidesExtent(TypedDict):
    type: ReadableValue[Literal[1]]
    side_one: str  # "-2.00 in"
    side_two: str  # "1 in"


class SymmetricExtent(TypedDict):
    type: ReadableValue[Literal[2]]
    distance: str  # "1 in"
    isFullLength: bool


ExtrudeExtent = OneSideExtent | TwoSidesExtent | SymmetricExtent


class ExtrudeDetails(TypedDict):
    operation: ReadableValue[Literal[0, 1, 2, 3, 4]]  # Cut=0, Join=1, Intersect=2, NewBody=3, CutIntersect=4
    extent: ExtrudeExtent | Error


class ExtrudeFeature(TypedDict):
    name: str
    type: ReadableValue[Literal["adsk::fusion::ExtrudeFeature"]]
    details: ExtrudeDetails | Error
