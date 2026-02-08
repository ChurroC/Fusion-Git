from typing import Literal, TypedDict
from ..utils_type import Error, ReadableValue


class ComponentDetails(TypedDict):
    id: str


class ComponentFeature(TypedDict):
    index: int
    name: str
    type: ReadableValue[Literal["adsk::fusion::Occurrence"]]
    details: ComponentDetails | Error
