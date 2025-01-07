# Author - ChurroC
# Description - Export timeline data to a JSON file
# type: ignore

from typing import Literal, cast
import adsk.core, adsk.fusion
import os

from .globals.globals import ui, units_manager, design, error, print_fusion, root
from .globals.types import (
    Timeline,
    Feature,
    SketchFeature,
    ExtrudeFeature,
    Error,
    ComponentFeature,
    FusionComponentTimeline,
)
from .display_data import write_to_file
from .features import get_sketch_data, get_extrude_data
from .globals.utils import create_readable_value
from .get_component_timeline import get_component_timeline_data

src_folder_path: str = 4

# Options in case they don't wish to store the data in the default location - which is root
output_folder = "data"


def run(context):
    try:
        print_fusion("")
        print_fusion("")
        print_fusion("")
        print_fusion("")

        folderDialog = ui.createFolderDialog()
        folderDialog.title = "Save Timeline Export"
        folderDialog.initialDirectory = "data"  # Hmmm doesn't seem to wrok

        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        global src_folder_path
        src_folder_path = folderDialog.folder

        component_timeline = get_component_timeline_data()

        read_timeline()

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


def read_timeline(doc=design) -> FusionComponentTimeline:
    data: Timeline = {
        "document_name": root.name,
        "units": create_readable_value(
            units_manager.defaultLengthUnits, cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits)
        ),
        "features": [],
    }
    doc.attributes.add("CHURRO-EXPORT", doc.rootComponent.id, "")

    for timeline_item in doc.timeline:
        entity = timeline_item.entity

        if hasattr(entity, "parentComponent"):  # This is a feature
            feature = cast(
                adsk.fusion.Feature, entity
            )  # If I try to cast using fusion api it deletes parentComponent for some reason
            parent_component = feature.parentComponent
            data[]
            component_timeline[parent_component.id].append(timeline_item)
        elif hasattr(
            entity, "sourceComponent"
        ):  # This is an occurrence - Reasons for an occurence - 1. creation of a component - 2. reference of a component (copy and paste) - 3. reference of a component (linked)
            occurrence = adsk.fusion.Occurrence.cast(entity)

            if (
                occurrence.component.id not in component_timeline and not occurrence.isReferencedComponent
            ):  # If this is the first occurence of the component we know that this is a creation - Cause copy paste needs the inital component to be created
                parent_path = doc.attributes.itemByName("CHURRO-EXPORT", occurrence.sourceComponent.id).value
                doc.attributes.add(
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
