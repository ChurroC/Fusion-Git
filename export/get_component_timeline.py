import os
from typing import cast
import adsk.core, adsk.fusion

from .globals.globals import design, print_fusion
from .globals.types import (
    FusionComponentTimeline,
)


def get_component_timeline_data() -> FusionComponentTimeline:
    component_timeline: FusionComponentTimeline = {design.rootComponent.id: []}
    design.attributes.add("CHURRO-EXPORT", design.rootComponent.id, "")

    for timeline_item in design.timeline:
        entity = timeline_item.entity

        if hasattr(entity, "parentComponent"):  # This is a feature
            feature = cast(
                adsk.fusion.Feature, entity
            )  # If I try to cast using fusion api it deletes parentComponent for some reason
            parent_component = feature.parentComponent
            component_timeline[parent_component.id].append(timeline_item)
        elif hasattr(
            entity, "sourceComponent"
        ):  # This is an occurrence - Reasons for an occurence - 1. creation of a component - 2. reference of a component (copy and paste) - 3. reference of a component (linked)
            occurrence = adsk.fusion.Occurrence.cast(entity)

            if (
                occurrence.component.id not in component_timeline and not occurrence.isReferencedComponent
            ):  # If this is the first occurence of the component we know that this is a creation - Cause copy paste needs the inital component to be created
                parent_path = design.attributes.itemByName("CHURRO-EXPORT", occurrence.sourceComponent.id).value
                design.attributes.add(
                    "CHURRO-EXPORT",
                    occurrence.component.id,
                    os.path.join(
                        parent_path,
                        f"{occurrence.timelineObject.index}{occurrence.component.name}-{occurrence.component.id}",
                    ),
                )

            component_timeline.setdefault(occurrence.component.id, [])
            component_timeline[occurrence.sourceComponent.id].append(
                timeline_item
            )  # Here we add it to the timeline of the parent component
    return component_timeline
