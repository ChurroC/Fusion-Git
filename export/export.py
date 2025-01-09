# Author - ChurroC
# Description - Export timeline data to a JSON file
# type: ignore

from html import entities
import json
import time
from typing import Literal, cast
import adsk.core, adsk.fusion
import os
from timeit import default_timer as timer


from .globals.globals import ui, units_manager, design, error, print_fusion, root
from .globals.compression import compress_json
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
        output_folder = os.path.basename(os.path.normpath(src_folder_path))

        data = read_timeline_data()
        data["json"] = compress_json(data)

        os.makedirs(os.path.dirname(src_folder_path), exist_ok=True)
        with open(os.path.join(src_folder_path, "timeline.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


def get_component_name(occurrence: adsk.fusion.Occurrence, index: None | int = None) -> str:
    if index is None and occurrence.isReferencedComponent:
        return f"{occurrence.component.name}-{occurrence.component.id[:5]}"
    else:
        return f"{index}{occurrence.component.name}-{occurrence.component.id[:5]}"


def read_timeline_data(design=design):
    # Instead of storing data in fusion attributes using a dict here is going to be faster
    data = {
        "timeline": [],
        "components": {
            design.rootComponent.id: {
                "path": "",
                "is_linked": False,
                "name": design.rootComponent.name,
                "units": create_readable_value(
                    design.fusionUnitsManager.defaultLengthUnits,
                    cast(Literal[0, 1, 2, 3, 4], design.fusionUnitsManager.distanceDisplayUnits),
                ),
                "feature_index": [],
                "references": [],
            }
        },
    }

    for index, timeline_item in enumerate(design.timeline):
        print_fusion(index)
        entity = timeline_item.entity

        if hasattr(entity, "parentComponent"):  # This is a feature
            feature = cast(
                adsk.fusion.Feature, entity
            )  # If I try to cast using fusion api it deletes parentComponent for some reason
            data["timeline"].append(get_timeline_feature(timeline_item))
            data["components"][feature.parentComponent.id]["feature_index"].append(index)
        elif hasattr(
            entity, "sourceComponent"
        ):  # This is an occurrence - Reasons for an occurence - 1. creation of a component - 2. reference of a component (copy and paste) - 3. reference of a component (linked)
            occurrence = adsk.fusion.Occurrence.cast(entity)
            occurrence = cast(
                adsk.fusion.Occurrence, entity
            )  # If I try to cast using fusion api it deletes parentComponent for some reason

            data["timeline"].append(get_timeline_feature(timeline_item))

            # This is for the creation of a component
            if occurrence.component.id not in data["components"]:
                parent_path = data["components"][occurrence.sourceComponent.id]["path"]

                data["components"][occurrence.component.id] = {
                    "path": (
                        os.path.join(parent_path, get_component_name(occurrence))
                        if not occurrence.isReferencedComponent
                        else os.path.join("linked_components", get_component_name(occurrence, timeline_item))
                    ),
                    "is_linked": occurrence.isReferencedComponent,
                    "name": design.rootComponent.name,
                    "units": create_readable_value(
                        design.fusionUnitsManager.defaultLengthUnits,
                        cast(Literal[0, 1, 2, 3, 4], design.fusionUnitsManager.distanceDisplayUnits),
                    ),
                    "feature_index": [],
                    "references": [],
                }
                if occurrence.isReferencedComponent:
                    parent_path = data["components"][occurrence.sourceComponent.id]["path"]
                    data["components"][occurrence.component.id]["references"].append(
                        {
                            "name": occurrence.name,
                            "path": os.path.join(parent_path, get_component_name(occurrence, index)),
                        }
                    )
                    data["components"][occurrence.component.id]["assembly"] = read_timeline_data(
                        occurrence.component.parentDesign
                    )
            else:  # Copy basically
                parent_path = data["components"][occurrence.sourceComponent.id]["path"]
                data["components"][occurrence.component.id]["references"].append(
                    {
                        "name": occurrence.name,
                        "path": os.path.join(parent_path, get_component_name(occurrence, index)),
                    }
                )

            data["components"][occurrence.sourceComponent.id]["feature_index"].append(index)
    return data


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
