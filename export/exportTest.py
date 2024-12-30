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
)
from .display_data import write_to_file
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

        print_fusion("")
        print_fusion("")
        print_fusion("")
        print_fusion("")

        global component_timeline
        component_timeline = get_component_timeline_data()

        # This is just so I can tell the names of the compoentn using their ids
        lookup = {design.rootComponent.id: design.rootComponent.name}

        for occ in design.rootComponent.allOccurrences:
            lookup[occ.component.id] = occ.component.name

        for component_id, component_timeline_item in component_timeline.items():
            print_fusion("Component: " + lookup[component_id])
            # Print out this file strucure to print_fusion
            for timeline_item in component_timeline_item:
                print_fusion(
                    f"\t{timeline_item['name']} --- is linked: {timeline_item['is_linked']} --- is component creation: {timeline_item['is_component_creation']} --- path: {timeline_item['path']} --- parent path: {timeline_item['parent_path']}",
                )

        write_component_data_to_file(design.rootComponent.id, src_folder_path, "")

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


# def get_file_name(occurence: adsk.fusion.Occurrence) -> str:
#     return f"{occurence.timelineObject.index}{occurence.component.name}"


# def get_component_path(occurrence: adsk.fusion.Occurrence) -> str:

#     print_fusion("")
#     current = occurrence
#     path_segments = [get_file_name(occurrence)]

#     try:
#         print_fusion(current.assemblyContext.name)
#     except:
#         print_fusion("Root")
#     print_fusion(current.sourceComponent.name, design.rootComponent.name)
#     # Build path from current occurrence up to root
#     while current.sourceComponent != design.rootComponent:
#         print_fusion(current.sourceComponent.name, design.rootComponent.name)
#         path_segments.append(get_file_name(current))
#         for occ in design.rootComponent.allOccurrencesByComponent(current.sourceComponent):
#             if occ.component == current.sourceComponent:
#                 current = occ

#     return "/".join(path_segments[::-1])


def get_component_timeline_data() -> FusionComponentTimeline:
    component_timeline: FusionComponentTimeline = {design.rootComponent.id: []}

    first_occurrence_paths: dict[str, str] = {}

    for timeline_item in design.timeline:
        entity = timeline_item.entity

        if hasattr(entity, "parentComponent"):  # This is a feature
            feature = cast(
                adsk.fusion.Feature, entity
            )  # If I try to cast using fusion api it deletes parentComponent for some reason
            parent_component = feature.parentComponent
            component_timeline[parent_component.id].append(
                {
                    "is_linked": False,
                    "is_component_creation": False,
                    "path": None,  # Features don't need paths
                    "parent_path": None,
                    "name": feature.name,
                    "timeline_item": timeline_item,
                }
            )
        elif hasattr(
            entity, "sourceComponent"
        ):  # This is an occurrence - Reasons for an occurence - 1. creation of a component - 2. reference of a component (copy and paste) - 3. reference of a component (linked)
            occurrence = adsk.fusion.Occurrence.cast(entity)

            is_component_creation = (
                occurrence.component.id not in component_timeline
            )  # If this is the first occurence of the component we know that this is a creation - Cause copy paste needs the inital component to be created
            path = occurrence.fullPathName

            if is_component_creation:
                first_occurrence_paths[occurrence.component.id] = path

            component_timeline.setdefault(occurrence.component.id, [])

            # Here we add it to the timeline of the parent component
            component_timeline[
                occurrence.sourceComponent.id
            ].append(  # This is so we can add this occurence to the timline of the parent component
                {
                    "is_linked": occurrence.isReferencedComponent,
                    "is_component_creation": (
                        False if occurrence.isReferencedComponent else is_component_creation
                    ),  # If it is a reference we don't want to consider this as a creation
                    "path": path,
                    "parent_path": None if is_component_creation else first_occurrence_paths[occurrence.component.id],
                    "name": occurrence.name,
                    "timeline_item": timeline_item,
                }
            )

    def traverseAssembly(occurrences: adsk.fusion.OccurrenceList, path):
        for occurrence in occurrences:
            component_timeline[occurrence.sourceComponent.id]
            path = path + "/" + occurrence.component.name
            if occurrence.childOccurrences:
                inputString = traverseAssembly(occurrence.childOccurrences, path)

    return component_timeline


def write_component_data_to_file(component_id: str, folder_path: str, folder_name: str, component_reference=False):
    component_details = component_timeline[component_id]
    final_folder_path = os.path.join(folder_path, folder_name)

    data: Timeline = {
        "document_name": component_details["name"],
        "units": create_readable_value(
            units_manager.defaultLengthUnits, cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits)
        ),
        "features": [],
    }

    # Regular component with features
    if not component_reference and not component_details["is_linked"]:
        data["features"] = [
            get_timeline_feature(detail, final_folder_path) for detail in component_details["timeline_details"]
        ]
        write_to_file(os.path.join(final_folder_path, "timeline.md"), data)
        return

    # Component reference
    if component_reference:
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
            "link_to_component": f"[{component_details['name']}](/data4/linked_components/{folder_name.replace(' ', '%20')}/timeline.md/timeline.md)",
            "component_reference": False,
            "component_reference_id": component_id,
            "component_creation_name": component_details["name"],
        }
        write_to_file(os.path.join(folder_path, folder_name, "timeline.md"), data)


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
                f"{feature.index}{component.name}-{component.id}",
                True if not is_component_creation and not is_linked else False,
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
