from typing import NotRequired, TypedDict, Union, List
from .features.sketch_type import SketchFeature
from .features.extrude_type import ExtrudeFeature
from .utils_type import Error

Feature = Union[SketchFeature, ExtrudeFeature]

# This is gonna include component that is linked from the timeline
# Where I am going to have a folder in 
class LinkedComponent(TypedDict):
    name: str

# This is gonna include component custom made directly from the timeline
class Component(TypedDict):
    document_name: str
    units: int
    features: List[Union[Feature, Error]]
    child_components: NotRequired[List[Union['Component', LinkedComponent, Error]]] # Recursive type
