from typing import Literal, TypedDict
from ..utils_type import Error, ReadableValue


class ComponentDetails(TypedDict):
    is_component_creation: bool
    is_linked: bool
    id: str


class ComponentFeature(TypedDict):
    name: str
    type: ReadableValue[Literal["adsk::fusion::Occurrence"]]
    details: ComponentDetails | Error
