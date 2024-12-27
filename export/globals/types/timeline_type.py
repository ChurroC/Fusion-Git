from typing import Literal, NotRequired, TypedDict
import adsk.fusion

from .features.sketch_feature_type import SketchFeature
from .features.extrude_feature_type import ExtrudeFeature
from .features.component_feature_type import ComponentFeature
from .utils_type import Error

Feature = SketchFeature | ExtrudeFeature | ComponentFeature


# This is going to be our timeline data export structure
class Timeline(TypedDict):
    document_name: str
    units: NotRequired[Literal[0, 1, 2, 3, 4]]
    features: list[Feature | Error]


class TimelineDetails(TypedDict):
    is_linked: bool
    is_component_creation: bool
    timeline_item: adsk.fusion.TimelineObject


class FusionComponentDetails(TypedDict):
    is_root: bool
    is_linked: bool
    name: str
    timeline: list[TimelineDetails]


FusionComponentTimeline = dict[str, FusionComponentDetails]  # This is going to be out version of the fusion timeline
