from typing import NotRequired, TypedDict
import adsk.fusion

from .features.sketch_feature_type import SketchFeature
from .features.extrude_feature_type import ExtrudeFeature
from .features.component_feature_type import ComponentFeature
from .utils_type import Error

Feature = SketchFeature | ExtrudeFeature | ComponentFeature

# This is going to be our timeline data export structure
class Timeline(TypedDict):
    document_name: str
    units: NotRequired[int]
    features: list[Feature | Error]

class FusionComponentTimelineDetails(TypedDict):
    is_root: bool
    is_linked: bool
    name: str
    components: list[adsk.fusion.TimelineObject]
FusionComponentTimeline = dict[str, FusionComponentTimelineDetails] # This is going to be out version of the fusion timeline