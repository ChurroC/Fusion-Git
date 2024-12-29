from typing import Literal, NotRequired, TypedDict

from .features.sketch_feature_type import SketchFeature
from .features.extrude_feature_type import ExtrudeFeature
from .features.component_feature_type import ComponentFeature
from .utils_type import Error, ReadableValue

Feature = SketchFeature | ExtrudeFeature | ComponentFeature


class TimelineInfo(TypedDict):
    link_to_component: str
    component_reference: bool
    component_reference_id: str
    component_creation_name: str


# This is going to be our timeline output json
class Timeline(TypedDict):
    document_name: str
    units: NotRequired[ReadableValue[Literal[0, 1, 2, 3, 4]]]
    info: NotRequired[TimelineInfo]
    features: list[Feature | Error]
    json: NotRequired[str]