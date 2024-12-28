from typing import Generic, TypeVar, TypedDict


class Error(TypedDict):
    error: str


class Point3D(TypedDict):
    x: str
    y: str
    z: str


T = TypeVar("T")


class ReadableValue(TypedDict, Generic[T]):
    md: str
    value: T
