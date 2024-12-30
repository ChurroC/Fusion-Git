import adsk.fusion
from typing import TypedDict


class ComponentTimelineItem(TypedDict):
    is_linked: bool  # This is going to show if the current component creation is linked
    is_component_creation: bool
    path: str | None
    parent_path: str | None
    name: str
    timeline_item: adsk.fusion.TimelineObject


FusionComponentTimeline = dict[
    str, list[ComponentTimelineItem]
]  # This is going to be out version of the fusion timeline
