from typing import TypedDict
import adsk.fusion

from .features.sketch_feature_type import SketchFeature
from .features.extrude_feature_type import ExtrudeFeature
from .features.component_feature_type import ComponentFeature
from .utils_type import Error

Feature = SketchFeature | ExtrudeFeature | ComponentFeature

# This is going to be our timeline data export structure
class Timeline(TypedDict):
    document_name: str
    units: int
    features: list[Feature | Error]

FusionComponentTimeline = dict[str, list[adsk.fusion.TimelineObject]] # This is going to be out version of the fusion timeline