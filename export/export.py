# Author - ChurroC
# Description - Export timeline data to a JSON file

from calendar import c
from operator import is_
from typing import Literal, cast
import adsk.core, adsk.fusion
import os

from .globals.globals import app, ui, units_manager, design, error, print_fusion
from .globals.types.types import (
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
from .features.features import get_sketch_data, get_extrude_data

component_timeline: FusionComponentTimeline
src_folder_path: str


def run(context):
    try:
        folderDialog = ui.createFolderDialog()
        folderDialog.title = "Save Timeline Export"
        folderDialog.initialDirectory = "data"  # Hmmm doesn't seem to wrok

        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        global src_folder_path
        src_folder_path = folderDialog.folder

        global component_timeline
        component_timeline = get_component_timeline_data()

        # This is just for me to check out the data structure of component timeline
        """
        for component_id, component_details in component_timeline.items():
            # Print out this file strucure to print_fusion
            print_fusion(
                f"Component {component_details['name']} is root: {component_details['is_root']} is linked: {component_details['is_linked']}"
            )
            for timeline_item in component_details["timeline"]:
                print_fusion(
                    f"\t{timeline_item['timeline_item'].name} --- is linked: {timeline_item['is_linked']} --- is component creation: {timeline_item['is_component_creation']}",
                )
        """

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
        parent_component_id = None
        is_component_creation = False
        is_linked = False

        if hasattr(entity, "parentComponent"):
            parent_component = cast(
                adsk.fusion.Feature, entity
            ).parentComponent  # If I try to cast using fusion api it deletes parentComponent for some reason
            parent_component_id = parent_component.id
        elif hasattr(entity, "sourceComponent"):
            occurrence = adsk.fusion.Occurrence.cast(entity)
            parent_component_id = occurrence.sourceComponent.id
            component_id = occurrence.component.id
            # This is when an occurance of a component occurs
            # We need to check if the component is already in our custom timeline
            if component_id not in component_timeline:
                is_linked = occurrence.isReferencedComponent
                is_component_creation = True if not is_linked else False

                parent_path = component_timeline[parent_component_id]["path"]
                component_path = os.path.join(parent_path, f"{occurrence.component.name}-{component_id}")

                component_timeline[component_id] = {
                    "is_root": False,
                    "is_linked": occurrence.isReferencedComponent,
                    "path": component_path,
                    "name": occurrence.component.name,
                    "timeline_details": [],
                }

        if parent_component_id:
            component_timeline[parent_component_id]["timeline_details"].append(
                {
                    "is_linked": is_linked,
                    "is_component_creation": is_component_creation,
                    "timeline_item": timeline_item,
                }
            )

    return component_timeline


def write_component_data_to_file(component_id: str, folder_path: str, file_name: str, component_reference=False):
    component_details = component_timeline[component_id]
    is_linked = component_details["is_linked"]
    is_root = component_details["is_root"]
    timeline_details = component_details["timeline_details"]

    final_folder_path = os.path.join(folder_path, file_name)

    if is_linked:
        final_folder_path = os.path.join(src_folder_path, "linked_components", file_name, "timeline.md")
    data: Timeline = {
        "document_name": component_details["name"],
        "units": cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits),
        "features": [],
    }

    if not component_reference:
        for timeline_detail in timeline_details:
            data["features"].append(get_timeline_feature(timeline_detail, final_folder_path))
    elif not is_linked:
        backslash_char = "\\"
        data["info"] = {
            "link": f"[{component_details['name']}]({component_details['path'].replace(' ', '%20').replace(backslash_char, '/')}/timeline.md)",
            "component_reference": component_reference,
            "component_reference_id": component_id,
            "component_creation_name": component_details["name"],
        }

    write_to_file(os.path.join(final_folder_path, "timeline.md"), data)

    if is_linked:
        data["info"] = {
            "link": f"[{component_details['name']}](/data4/linked_components/{file_name.replace(' ', '%20')}/timeline.md/timeline.md)",
            "component_reference": component_reference,
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
                "type": cast(Literal["adsk::fusion::Sketch"], feature_type),
                "details": get_sketch_data(extrude),
            }
            return sketch_feature_data
        elif feature_type == adsk.fusion.ExtrudeFeature.classType():
            sketch = adsk.fusion.ExtrudeFeature.cast(entity)
            extrude_feature_data: ExtrudeFeature = {
                "name": sketch.name,
                "type": cast(Literal["adsk::fusion::ExtrudeFeature"], feature_type),
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
                "name": component.name,
                "type": cast(Literal["adsk::fusion::Occurrence"], feature_type),
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
