# Author - ChurroC
# Description - Export timeline data to a JSON file

from typing import Literal, cast
import adsk.core, adsk.fusion
import os

from .globals.globals import ui, units_manager, design, error, print_fusion
from .globals.types import (
    Timeline,
    Feature,
    SketchFeature,
    ExtrudeFeature,
    Error,
    ComponentFeature,
    FusionComponentTimeline,
    TimelineDetail,
)
from .json_to_markdown import write_to_file
from .features import get_sketch_data, get_extrude_data
from .globals.utils import create_readable_value

component_timeline: FusionComponentTimeline


def run(context):
    try:
        folderDialog = ui.createFolderDialog()
        folderDialog.title = "Save Timeline Export"
        folderDialog.initialDirectory = "data"  # Hmmm doesn't seem to wrok

        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        src_folder_path = folderDialog.folder

        global component_timeline
        component_timeline = get_component_timeline_data()

        for component_id, component_details in component_timeline.items():
            # Print out this file strucure to print_fusion
            print_fusion(
                f"Component {component_details['name']} is root: {component_details['is_root']} is linked: {component_details['is_linked']}"
            )
            for timeline_item in component_details["timeline_details"]["timeline"]:
                print_fusion(
                    f"\t{timeline_item['timeline_item'].name} --- is linked: {timeline_item['is_linked']} --- is component creation: {timeline_item['is_component_creation']}",
                )

        write_component_data_to_file(design.rootComponent.id, src_folder_path, "")

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


def get_component_timeline_data() -> FusionComponentTimeline:
    component_timeline: FusionComponentTimeline = {
        design.rootComponent.id: {
            "is_root": True,
            "is_linked": False,
            "path": "/data4/",
            "name": design.rootComponent.name,
            "timeline_details": [],
        }
    }

    for timeline_item in design.timeline:
        entity = timeline_item.entity

        if hasattr(entity, "parentComponent"):  # This is a feature
            parent_component = cast(
                adsk.fusion.Feature, entity
            ).parentComponent  # If I try to cast using fusion api it deletes parentComponent for some reason
            component_timeline[parent_component.id]["timeline_details"].append(
                {
                    "is_linked": False,
                    "is_component_creation": False,
                    "timeline_item": timeline_item,
                }
            )
        elif hasattr(
            entity, "sourceComponent"
        ):  # This is an occurrence - 1. creation of a component - 2. reference of a component (copy and paste) - 3. reference of a component (linked)
            occurrence = adsk.fusion.Occurrence.cast(entity)
            parent_component_id = (
                occurrence.sourceComponent.id
            )  # This is so we can add this occurence to the timline of the parent component
            component_id = (
                occurrence.component.id
            )  # This is the id of the component that is being referenced from the occurence

            is_component_creation = False
            # If this occurence happens for the first time we know that this is the creation of the component since we are iterating through the timeline
            # If we iterate through the timeline we must have a creation occur before a reference (reference are basically copy and pastes)
            if component_id not in component_timeline:
                parent_path = component_timeline[parent_component_id]["path"]
                component_path = os.path.join(parent_path, f"{occurrence.component.name}-{component_id}")
                is_component_creation = True

                component_timeline[component_id] = {
                    "is_root": False,
                    "is_linked": occurrence.isReferencedComponent,
                    "path": component_path,
                    "name": occurrence.component.name,
                    "timeline_details": [],
                }

            # Here we add it to the timeline of the parent component
            component_timeline[parent_component_id]["timeline_details"].append(
                {
                    "is_linked": occurrence.isReferencedComponent,
                    "is_component_creation": (
                        is_component_creation if not occurrence.isReferencedComponent else False
                    ),  # If it is a reference we don't want to consider this as a creation
                    "timeline_item": timeline_item,
                }
            )

    return component_timeline


def write_component_data_to_file(component_id: str, folder_path: str, file_name: str, component_reference=False):
    component_details = component_timeline[component_id]
    final_folder_path = os.path.join(folder_path, file_name)

    data: Timeline = {
        "document_name": component_details["name"],
        "units": create_readable_value(
            units_manager.defaultLengthUnits, cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits)
        ),
        "features": [],
    }
    print_fusion("")
    print_fusion(component_details["name"])
    print_fusion(component_reference, component_details["is_linked"])
    # Regular component with features
    if not component_reference and not component_details["is_linked"]:
        data["features"] = [
            get_timeline_feature(detail, final_folder_path) for detail in component_details["timeline_details"]
        ]
        write_to_file(os.path.join(final_folder_path, "timeline.md"), data)
        return

    # Component reference
    if component_reference:
        print_fusion(component_details["name"])
        data["info"] = {
            "link_to_component": f"[{component_details['name']}]({component_details['path'].replace(' ', '%20').replace('\\', '/')}/timeline.md)",
            "component_reference": True,
            "component_reference_id": component_id,
            "component_creation_name": component_details["name"],
        }
        write_to_file(os.path.join(final_folder_path, "timeline.md"), data)
        return

    # Linked component
    if component_details["is_linked"]:
        data["info"] = {
            "link_to_component": f"[{component_details['name']}](/data4/linked_components/{file_name.replace(' ', '%20')}/timeline.md/timeline.md)",
            "component_reference": False,
            "component_reference_id": component_id,
            "component_creation_name": component_details["name"],
        }
        write_to_file(os.path.join(folder_path, file_name, "timeline.md"), data)


def get_timeline_feature(timeline_detail: TimelineDetail, folder_path) -> Feature | Error:
    is_linked = timeline_detail["is_linked"]
    is_component_creation = timeline_detail["is_component_creation"]
    feature = timeline_detail["timeline_item"]
    try:
        entity = feature.entity
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

            write_component_data_to_file(
                component.id,
                folder_path,
                f"{component.name}-{component.id}",
                True if not is_component_creation else False,
            )

            component_feature_data: ComponentFeature = {
                "name": occurrence.name,
                "type": create_readable_value(
                    "Component Occurence", cast(Literal["adsk::fusion::Occurrence"], feature_type)
                ),
                "details": {
                    "is_linked": occurrence.isReferencedComponent,
                    "is_component_creation": is_component_creation,
                    "id": component.id,
                },
            }
            return component_feature_data
        else:
            raise Exception("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature", e)
