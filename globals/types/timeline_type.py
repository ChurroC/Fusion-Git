from typing import TypedDict, Union, List
from .features.sketch_feature_type import SketchFeature
from .features.extrude_feature_type import ExtrudeFeature
from .features.component_feature_type import ComponentFeature
from .utils_type import Error

Feature = SketchFeature | ExtrudeFeature | ComponentFeature

# This is gonna include component custom made directly from the timeline
class Timeline(TypedDict):
    document_name: str
    units: int
    features: List[Union[Feature, Error]]

# child_components: NotRequired[List[Union['Timeline', LinkedComponent, Error]]] # Recursive type
