from typing import Generic, Literal, TypeVar, TypedDict


class Error(TypedDict):
    error: str


Value = TypeVar("Value")


class NoMarkdown(TypedDict, Generic[Value]):
    display: Literal[False]
    value: Value


class ReadableValue(TypedDict, Generic[Value]):
    md: str
    value: Value


class Point3DValue(TypedDict):
    x: str
    y: str
    z: str


Point3D = ReadableValue[Point3DValue]
