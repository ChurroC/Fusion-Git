from typing import Literal, NotRequired, TypedDict
import adsk.fusion

from .features.sketch_feature_type import SketchFeature
from .features.extrude_feature_type import ExtrudeFeature
from .features.component_feature_type import ComponentFeature
from .utils_type import Error, ReadableValue

Feature = SketchFeature | ExtrudeFeature | ComponentFeature


class TimelineInfo(TypedDict):
    link: str
    component_reference: bool
    component_reference_id: str
    component_creation_name: str


# This is going to be our timeline data export structure
class Timeline(TypedDict):
    document_name: str
    units: NotRequired[ReadableValue[Literal[0, 1, 2, 3, 4]]]
    info: NotRequired[TimelineInfo]
    features: list[Feature | Error]


class TimelineDetail(TypedDict):
    is_linked: bool  # This is going to show if the current component creation is linked
    is_component_creation: bool
    timeline_item: adsk.fusion.TimelineObject


class FusionComponentDetails(TypedDict):
    path: str
    is_root: bool
    is_linked: bool  # This is going to see if the parent component of this timeline is linked
    name: str
    timeline_details: list[TimelineDetail]


FusionComponentTimeline = dict[str, FusionComponentDetails]  # This is going to be out version of the fusion timeline
