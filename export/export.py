# Author - ChurroC
# Description - Export timeline data to a JSON file
""" # type: ignore """

from typing import Literal, cast
import adsk.core, adsk.fusion
import json
import os

# from timeit import default_timer as timer

from .globals.globals import ui, design, error, print_fusion
from .globals.utils import create_readable_value, compress_json, create_no_markdown
from .globals.types import (
    Data,
    Feature,
    SketchFeature,
    ExtrudeFeature,
    Error,
    ComponentFeature,
)
from .features import get_sketch_data, get_extrude_data
from .write_data import write_nested_data


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

        src_folder_path = folderDialog.folder

        folder_path_in_git = os.path.basename(os.path.normpath(src_folder_path))

        data = read_timeline_data(folder_path_in_git)
        write_nested_data(src_folder_path, data)

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


# Chnage to occurence name
def get_component_name(occurrence: adsk.fusion.Occurrence, index: None | int = None) -> str:
    if index is None:
        if occurrence.isReferencedComponent:
            return f"{occurrence.component.name}-{occurrence.component.id[:5]}"
        else:
            return f"{occurrence.timelineObject.index}{occurrence.component.name}-{occurrence.component.id[:5]}"
    else:
        return f"{index}{occurrence.component.name}-{occurrence.component.id[:5]}"


def read_timeline_data(
    folder_path_in_git: str = "",
    path: str = "",
    design=design,
):
    # Instead of storing data in fusion attributes using a dict here is going to be faster
    data: Data = {
        "timeline": [],
        "components": {
            design.rootComponent.id: {
                "index": 0,
                "path": path,
                "is_linked": False,
                "name": design.rootComponent.name,
                "units": create_readable_value(
                    design.fusionUnitsManager.defaultLengthUnits,
                    cast(Literal[0, 1, 2, 3, 4], design.fusionUnitsManager.distanceDisplayUnits),
                ),
                "features": [],
                "references": [],
            }
        },
    }

    for index, timeline_item in enumerate(design.timeline):
        entity = timeline_item.entity

        if hasattr(entity, "parentComponent"):  # This is a feature
            feature = cast(
                adsk.fusion.Feature, entity
            )  # If I try to cast using fusion api it deletes parentComponent for some reason
            feature_info = get_timeline_feature(timeline_item)
            data["timeline"].append(feature_info)
            data["components"][feature.parentComponent.id]["features"].append(feature_info)
        elif hasattr(
            entity, "sourceComponent"
        ):  # This is an occurrence - Reasons for an occurence - 1. creation of a component - 2. reference of a component (copy and paste) - 3. reference of a component (linked)
            occurrence = adsk.fusion.Occurrence.cast(entity)

            feature_info = get_timeline_feature(timeline_item)
            data["timeline"].append(feature_info)

            # This is for the creation of a component
            if occurrence.component.id not in data["components"]:
                parent_path = data["components"][occurrence.sourceComponent.id]["path"]
                linked_path = os.path.join(
                    data["components"][design.rootComponent.id]["path"],
                    "linked_components",
                    get_component_name(occurrence, index),
                )

                data["components"][occurrence.component.id] = {
                    "index": index,
                    "path": (
                        os.path.join(parent_path, get_component_name(occurrence))
                        if not occurrence.isReferencedComponent
                        else linked_path
                    ),
                    "is_linked": occurrence.isReferencedComponent,
                    "name": design.rootComponent.name,
                    "features": [],
                    "references": [],
                }
                if occurrence.isReferencedComponent:
                    # Since I have the orgininal component path in linked_component
                    # I can just add the reference to the linked component
                    parent_path = data["components"][occurrence.sourceComponent.id]["path"]
                    original_component_path = os.path.join(
                        folder_path_in_git, data["components"][occurrence.component.id]["path"]
                    )
                    component_path = os.path.join(
                        folder_path_in_git, parent_path, get_component_name(occurrence, index)
                    )
                    data["components"][occurrence.component.id]["references"].append(
                        {
                            "name": occurrence.name,
                            "path": os.path.join(parent_path, get_component_name(occurrence, index)),
                            "link_to_reference": f"[{occurrence.name}](/{component_path.replace(' ', '%20').replace('\\', '/')}/timeline.md)",
                            "link_to_component": f"[{occurrence.component.name}](/{original_component_path.replace(' ', '%20').replace('\\', '/')}/timeline.md)",
                        }
                    )
                    # I also traverse the assembly within the linked component
                    data["components"][occurrence.component.id]["assembly"] = create_no_markdown(
                        read_timeline_data(
                            folder_path_in_git,
                            linked_path,
                            occurrence.component.parentDesign,
                        )
                    )
            else:  # Copy basically
                parent_path = data["components"][occurrence.sourceComponent.id]["path"]
                original_component_path = os.path.join(
                    folder_path_in_git, data["components"][occurrence.component.id]["path"]
                )
                component_path = os.path.join(folder_path_in_git, parent_path, get_component_name(occurrence, index))
                data["components"][occurrence.component.id]["references"].append(
                    {
                        "name": occurrence.name,
                        "path": os.path.join(parent_path, get_component_name(occurrence, index)),
                        "link_to_reference": f"[{occurrence.name}](/{component_path.replace(' ', '%20').replace('\\', '/')}/timeline.md)",
                        "link_to_component": f"[{occurrence.component.name}](/{original_component_path.replace(' ', '%20').replace('\\', '/')}/timeline.md)",
                    }
                )

            data["components"][occurrence.sourceComponent.id]["features"].append(feature_info)
    return data


def get_timeline_feature(timeline_feature: adsk.fusion.TimelineObject) -> Feature | Error:
    try:
        entity = timeline_feature.entity
        feature_type = entity.objectType

        if feature_type == adsk.fusion.Sketch.classType():
            extrude = adsk.fusion.Sketch.cast(entity)
            sketch_feature_data: SketchFeature = {
                "index": timeline_feature.index,
                "name": extrude.name,
                "type": create_readable_value("Sketch", cast(Literal["adsk::fusion::Sketch"], feature_type)),
                "details": get_sketch_data(extrude),
            }
            return sketch_feature_data
        elif feature_type == adsk.fusion.ExtrudeFeature.classType():
            sketch = adsk.fusion.ExtrudeFeature.cast(entity)
            extrude_feature_data: ExtrudeFeature = {
                "index": timeline_feature.index,
                "name": sketch.name,
                "type": create_readable_value("Extrude", cast(Literal["adsk::fusion::ExtrudeFeature"], feature_type)),
                "details": get_extrude_data(sketch),
            }
            return extrude_feature_data
        elif feature_type == adsk.fusion.Occurrence.classType():
            occurrence = adsk.fusion.Occurrence.cast(entity)
            component = occurrence.component
            component_feature_data: ComponentFeature = {
                "index": timeline_feature.index,
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
