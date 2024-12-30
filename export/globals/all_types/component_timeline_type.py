import adsk.fusion
from typing import TypedDict


class ComponentTimelineItem(TypedDict):
    is_linked: bool  # This is going to show if the current component creation is linked
    name: str
    timeline_item: adsk.fusion.TimelineObject


FusionComponentTimeline = dict[
    str, list[adsk.fusion.TimelineObject]
]  # This is going to be out version of the fusion timeline
