from typing import Generic, NotRequired, TypeVar, TypedDict
from .utils_type import ReadableValue


class Error(TypedDict):
    error: str


class Point3DValue(TypedDict):
    x: str
    y: str
    z: str


Point3D = ReadableValue[Point3DValue]


T = TypeVar("T")


class ReadableValue(TypedDict, Generic[T]):
    md: str
    display: NotRequired[bool]
    value: T
