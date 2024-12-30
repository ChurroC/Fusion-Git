# Author - ChurroC
# Description - Export timeline data to a JSON file
""" # type: ignore """

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

src_folder_path: str
component_timeline: FusionComponentTimeline

# Options in case they don't wish to store the data in the default location - which is root
output_folder = "data5"


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

        global component_timeline
        component_timeline = get_component_timeline_data()

        data: Timeline = {
            "document_name": root.name,
            "units": create_readable_value(
                units_manager.defaultLengthUnits, cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits)
            ),
            "features": [get_timeline_feature(timeline_feature) for timeline_feature in component_timeline[root.id]],
        }
        write_to_file(os.path.join(src_folder_path, "timeline.md"), data)

        traverseAssembly(root.occurrences.asList, "")

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


def traverseAssembly(occurrences: adsk.fusion.OccurrenceList, path):
    for occurrence in occurrences:
        try:
            # I check if component is not linked before adding occurrence.timelineObject.index since there seems to be an error in fusio
            # Also since a linked component will all reference the same component we're bing chilling - Since we need the index since the same level component
            # Could cause the folder to be overwritten as a reference - Which will never happen to a linked component since they all have the same folder
            folder_name = f"{occurrence.timelineObject.index if not occurrence.isReferencedComponent else ""}{occurrence.component.name}-{occurrence.component.id}"
            occurrence_path = os.path.join(path, folder_name)
            handle_occurrence(occurrence, occurrence_path)

            # If it's a linked component we don't want to read further in for now
            if occurrence.childOccurrences and not occurrence.isReferencedComponent:
                traverseAssembly(occurrence.childOccurrences, occurrence_path)
        except Exception as e:
            error("Failed to traverse assembly", e)


def handle_occurrence(occurrence: adsk.fusion.Occurrence, path):
    # First we need to check if this occurence is a component creation or a reference
    original_component_occurence = root.allOccurrencesByComponent(occurrence.component).item(0)
    if occurrence == original_component_occurence:
        # This is the creation of the component
        write_component_data_to_file(occurrence, path)
    else:
        if (
            not occurrence.isReferencedComponent
        ):  # Since if this is the second reference to a link it don't need to run cause it's in linked_components already
            write_component_data_to_file(occurrence, path, True)


def write_component_data_to_file(occurrence: adsk.fusion.Occurrence, folder_path: str, component_reference=False):
    data: Timeline = {
        "document_name": occurrence.component.name,
        "units": create_readable_value(
            units_manager.defaultLengthUnits, cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits)
        ),
        "features": [],
    }

    folder_path = os.path.join(src_folder_path, folder_path)

    # Regular component with features
    if not component_reference and not occurrence.isReferencedComponent:
        data["features"] = [
            get_timeline_feature(timeline_feature) for timeline_feature in component_timeline[occurrence.component.id]
        ]

    # Component reference
    # f"[{component_details['name']}]({component_details['path'].replace(' ', '%20').replace('\\', '/')}/timeline.md)"
    elif component_reference:
        data["info"] = {
            "link_to_component": f"[{occurrence.component.name}](/{os.path.join(output_folder, design.attributes.itemByName("CHURRO-EXPORT", occurrence.component.id).value, "timeline.md").replace(' ', '%20')})",
            "component_reference": True,
            "component_reference_id": occurrence.component.id,
        }

    # Linked component
    elif occurrence.isReferencedComponent:
        data["info"] = {
            "link_to_component": f"[{occurrence.component.name}](/{os.path.join(output_folder, "linked_components").replace(' ', '%20')}/timeline.md)",
            "component_reference": False,
            "component_reference_id": occurrence.component.id,
        }
        folder_path = os.path.join(src_folder_path, "linked_components")

    write_to_file(os.path.join(folder_path, "timeline.md"), data)


def get_timeline_feature(timeline_feature: adsk.fusion.TimelineObject) -> Feature | Error:
    try:
        entity = timeline_feature.entity
        feature_type = entity.objectType
        print("feature_type")
        print(feature_type)

        if feature_type == adsk.fusion.Sketch.classType():
            extrude = adsk.fusion.Sketch.cast(entity)
            sketch_feature_data: SketchFeature = {
                "name": extrude.name,
                "type": create_readable_value("Sketch", cast(Literal["adsk::fusion::Sketch"], feature_type)),
                "details": get_sketch_data(extrude),
            }
            return sketch_feature_data
        elif feature_type == adsk.fusion.ExtrudeFeature.classType():
            sketch = adsk.fusion.ExtrudeFeature.cast(entity)
            extrude_feature_data: ExtrudeFeature = {
                "name": sketch.name,
                "type": create_readable_value("Extrude", cast(Literal["adsk::fusion::ExtrudeFeature"], feature_type)),
                "details": get_extrude_data(sketch),
            }
            return extrude_feature_data
        elif feature_type == adsk.fusion.Occurrence.classType():
            occurrence = adsk.fusion.Occurrence.cast(entity)
            component = occurrence.component

            component_feature_data: ComponentFeature = {
                "name": occurrence.name,
                "type": create_readable_value(
                    "Component Occurence", cast(Literal["adsk::fusion::Occurrence"], feature_type)
                ),
                "details": {
                    "id": component.id,
                },
            }
            return component_feature_data
        else:
            raise Exception("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature", e)
