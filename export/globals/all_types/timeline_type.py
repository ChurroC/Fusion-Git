from typing import Literal, NotRequired, TypedDict

from .features.sketch_type import SketchFeature
from .features.extrude_type import ExtrudeFeature
from .features.component_type import ComponentFeature
from .utils_type import Error, ReadableValue

Feature = SketchFeature | ExtrudeFeature | ComponentFeature


class TimelineInfo(TypedDict):
    link_to_component: str
    component_reference: bool
    component_reference_id: str


# This is going to be our timeline output json
class Timeline(TypedDict):
    document_name: str
    units: NotRequired[ReadableValue[Literal[0, 1, 2, 3, 4]]]
    info: NotRequired[TimelineInfo]
    features: NotRequired[list[Feature | Error]]
    json: NotRequired[str]
