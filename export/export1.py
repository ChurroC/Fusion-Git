# Author - ChurroC
# Description - Export timeline data to a JSON file

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
)
from .globals.utils import write_to_file
from .features.features import get_sketch_data, get_extrude_data

component_timeline: FusionComponentTimeline


def run(context):
    try:
        folderDialog = ui.createFolderDialog()
        folderDialog.title = "Save Timeline Export"
        folderDialog.initialDirectory = "data"  # Hmmm doesn't seem to wrok

        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        folder_path = folderDialog.folder

        global component_timeline
        component_timeline = get_component_timeline_data()

        for component_id in component_timeline:
            data: Timeline = {
                "document_name": component_timeline[component_id]["name"],
                "units": cast(int, units_manager.defaultLengthUnits),
                "features": [],
            }
            if not component_timeline[component_id]["is_linked"] and not component_timeline[component_id]["is_root"]:
                del data["units"]

            file_path: str | None = None
            if component_timeline[component_id]["is_root"]:
                file_path = os.path.join(folder_path, "timeline.json")
            elif not component_timeline[component_id]["is_linked"]:
                file_path = os.path.join(
                    folder_path,
                    "components",
                    f"{component_timeline[component_id]['name']}-{component_id}.json",
                )
            elif component_timeline[component_id]["is_linked"]:
                file_path = os.path.join(
                    folder_path,
                    "linked_components",
                    f"{component_timeline[component_id]['name']}-{component_id}.json",
                )

            for timeline_item in component_timeline[component_id]["components"]:
                data["features"].append(get_timeline_feature(timeline_item))

            if file_path:
                write_to_file(file_path, data)

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


def get_component_timeline_data() -> FusionComponentTimeline:
    component_timeline: FusionComponentTimeline = {
        design.rootComponent.id: {
            "is_root": True,
            "is_linked": False,
            "name": design.rootComponent.name,
            "components": [],
        }
    }

    for timeline_item in design.timeline:
        entity = timeline_item.entity
        component_id = None

        if hasattr(entity, "parentComponent"):
            parent_component = cast(
                adsk.fusion.Feature, entity
            ).parentComponent  # If I try to cast using fusion api it deletes parentComponent for some reason
            component_id = parent_component.id
        elif hasattr(entity, "sourceComponent"):
            occurrence = adsk.fusion.Occurrence.cast(entity)
            source_component = occurrence.sourceComponent
            component_id = source_component.id
            # This is when an occurance of a component occurs
            # We need to check if the component is already in our custom timeline
            component_timeline[occurrence.component.id] = {
                "is_root": False,
                "is_linked": occurrence.isReferencedComponent,
                "name": occurrence.component.name,
                "components": [],
            }

        if component_id:
            component_timeline[component_id]["components"].append(timeline_item)

    return component_timeline


def get_timeline_feature(feature: adsk.fusion.TimelineObject) -> Feature | Error:
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
            component_feature_data: ComponentFeature = {
                "name": component.name,
                "type": cast(Literal["adsk::fusion::Occurrence"], feature_type),
                "details": {
                    "is_linked": occurrence.isReferencedComponent,
                    "id": component.id,
                },
            }
            return component_feature_data
        else:
            raise Exception("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature", e)
