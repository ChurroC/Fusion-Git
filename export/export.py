# Author - ChurroC
# Description - Export timeline data to a JSON file
# This is idea 2
""" # type: ignore """

from typing import Literal, cast
import adsk.core, adsk.fusion
import os
from timeit import default_timer as timer

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

# Options in case they don't wish to store the data in the default location - which is root
output_folder = "data_2"


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

        # write_nested_data(root.occurrences.asList, "", get_component_timeline_data())
        component_timeline, nested_data = get_component_timeline_data()

        start = timer()
        write_nested_data(nested_data, src_folder_path)
        end = timer()

        print_fusion(f"Function took {end - start} seconds")

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


def get_component_timeline_data(doc=design) -> tuple[FusionComponentTimeline, dict]:
    component_timeline: FusionComponentTimeline = {doc.rootComponent.id: []}
    # Root level data structure
    root_data = {
        "document_name": doc.rootComponent.name,
        "units": create_readable_value(
            units_manager.defaultLengthUnits, cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits)
        ),
        "features": [],
        "child_components": {},
        "linked_components": {},
    }

    # Track all components' data
    component_data_map = {doc.rootComponent.id: root_data}
    doc.attributes.add("CHURRO-EXPORT", doc.rootComponent.id, "")

    for timeline_item in doc.timeline:
        entity = timeline_item.entity

        if hasattr(entity, "parentComponent"):
            feature = cast(adsk.fusion.Feature, entity)
            parent_component = feature.parentComponent
            component_timeline[parent_component.id].append(timeline_item)

            # Add feature to parent component's data
            if parent_component.id in component_data_map:
                component_data_map[parent_component.id]["features"].append(get_timeline_feature(timeline_item))

        elif hasattr(entity, "sourceComponent"):
            occurrence = adsk.fusion.Occurrence.cast(entity)

            # Create new component data structure
            new_component_data = {
                "document_name": occurrence.component.name,
                "units": create_readable_value(
                    units_manager.defaultLengthUnits, cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits)
                ),
                "features": [],
                "child_components": {},
            }

            if occurrence.component.id not in component_timeline and not occurrence.isReferencedComponent:
                parent_path = doc.attributes.itemByName("CHURRO-EXPORT", occurrence.sourceComponent.id).value
                new_path = os.path.join(
                    parent_path,
                    f"{occurrence.timelineObject.index}{occurrence.component.name}-{occurrence.component.id}",
                )
                doc.attributes.add("CHURRO-EXPORT", occurrence.component.id, new_path)

                # Add to parent's child_components
                parent_data = component_data_map[occurrence.sourceComponent.id]
                if occurrence.isReferencedComponent:
                    parent_data["linked_components"][occurrence.component.id] = new_component_data
                else:
                    parent_data["child_components"][occurrence.component.id] = new_component_data

                component_data_map[occurrence.component.id] = new_component_data

            component_timeline.setdefault(occurrence.component.id, [])
            component_timeline[occurrence.sourceComponent.id].append(timeline_item)

            # Process occurrence data
            if occurrence.sourceComponent.id in component_data_map:
                component_data_map[occurrence.sourceComponent.id]["features"].append(
                    get_timeline_feature(timeline_item)
                )

    return component_timeline, root_data


def write_nested_data(data: dict, base_path: str):
    """Recursively write the nested data structure to files"""
    write_to_file(
        os.path.join(base_path, "timeline.md"),
        {"document_name": data["document_name"], "units": data["units"], "features": data["features"]},
    )

    # Write child components
    for comp_id, comp_data in data["child_components"].items():
        comp_path = os.path.join(base_path, f"{comp_id}")
        os.makedirs(comp_path, exist_ok=True)
        write_nested_data(comp_data, comp_path)

    # Write linked components
    if "linked_components" in data:
        linked_path = os.path.join(base_path, "linked_components")
        os.makedirs(linked_path, exist_ok=True)
        for comp_id, comp_data in data["linked_components"].items():
            comp_path = os.path.join(linked_path, f"{comp_id}")
            os.makedirs(comp_path, exist_ok=True)
            write_nested_data(comp_data, comp_path)


# def write_nested_data(data: dict, base_path: str):
#     """Write nested data efficiently using original folder naming"""
#     file_operations = []

#     def collect_file_ops(component_data: dict, current_path: str, timeline_index=""):
#         timeline_data = {
#             "document_name": component_data["document_name"],
#             "units": component_data["units"],
#             "features": component_data["features"],
#         }

#         # Add info for linked/referenced components
#         if "info" in component_data:
#             timeline_data["info"] = component_data["info"]

#         file_operations.append({"path": os.path.join(current_path, "timeline.md"), "data": timeline_data})

#         # Process child components
#         for comp_id, comp_data in component_data.get("child_components", {}).items():
#             # Use your original naming: {timeline_index}{component_name}-{component_id}
#             folder_name = f"{comp_data.get('timeline_index', '')}{comp_data['document_name']}-{comp_id}"
#             comp_path = os.path.join(current_path, folder_name)
#             collect_file_ops(comp_data, comp_path)

#         # Process linked components in the linked_components folder
#         for comp_id, comp_data in component_data.get("linked_components", {}).items():
#             folder_name = f"{comp_data.get('timeline_index', '')}{comp_data['document_name']}-{comp_id}"
#             comp_path = os.path.join(current_path, "linked_components", folder_name)
#             collect_file_ops(comp_data, comp_path)

#     # Collect all operations first
#     collect_file_ops(data, base_path)

#     # Create all directories at once
#     all_dirs = {os.path.dirname(op["path"]) for op in file_operations}
#     for dir_path in all_dirs:
#         os.makedirs(dir_path, exist_ok=True)

#     # Write all files
#     for op in file_operations:
#         write_to_file(op["path"], op["data"])


# def write_nested_data(data: dict, base_path: str):
#     """Write nested data with optimized directory creation"""
#     file_operations = []

#     def collect_file_ops(component_data: dict, current_path: str):
#         # Create directory immediately as we traverse
#         os.makedirs(current_path, exist_ok=True)

#         # Add file operation
#         file_operations.append(
#             {
#                 "path": os.path.join(current_path, "timeline.md"),
#                 "data": {
#                     "document_name": component_data["document_name"],
#                     "units": component_data["units"],
#                     "features": component_data["features"],
#                 },
#             }
#         )

#         # Process children with directories created during traversal
#         for comp_id, comp_data in component_data.get("child_components", {}).items():
#             folder_name = f"{comp_data.get('timeline_index', '')}{comp_data['document_name']}-{comp_id}"
#             comp_path = os.path.join(current_path, folder_name)
#             collect_file_ops(comp_data, comp_path)

#         # Process linked components
#         for comp_id, comp_data in component_data.get("linked_components", {}).items():
#             folder_name = f"{comp_data.get('timeline_index', '')}{comp_data['document_name']}-{comp_id}"
#             linked_path = os.path.join(current_path, "linked_components")
#             os.makedirs(linked_path, exist_ok=True)  # Create linked_components folder
#             comp_path = os.path.join(linked_path, folder_name)
#             collect_file_ops(comp_data, comp_path)

#     # Collect operations and create directories during traversal
#     collect_file_ops(data, base_path)

#     # Batch only the file writes
#     for op in file_operations:
#         write_to_file(op["path"], op["data"])


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
