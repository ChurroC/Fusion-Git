import adsk.fusion
from typing import TypedDict


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
