# Author - ChurroC
# Description - Export timeline data to a JSON file
# type: ignore

from html import entities
import json
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
        os.makedirs(os.path.dirname(src_folder_path), exist_ok=True)
        with open(os.path.join(src_folder_path, "timeline.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)


def get_component_name(occurrence: adsk.fusion.Occurrence) -> str:
    return f"{occurrence.timelineObject.index}{occurrence.component.name}-{occurrence.component.id}"


def read_timeline_data(design=design):
    # Instead of storing data in fusion attributes using a dict here is going to be faster
    data = {
        design.rootComponent.id: {
            "path": "",
            "name": design.rootComponent.name,
            "units": create_readable_value(
                design.fusionUnitsManager.defaultLengthUnits,
                cast(Literal[0, 1, 2, 3, 4], design.fusionUnitsManager.distanceDisplayUnits),
            ),
            "features": [],
            "references": [],
        }
    }

    for timeline_item in design.timeline:
        entity = timeline_item.entity

        if hasattr(entity, "parentComponent"):  # This is a feature
            feature = cast(
                adsk.fusion.Feature, entity
            )  # If I try to cast using fusion api it deletes parentComponent for some reason
            parent_component = feature.parentComponent
            # print_fusion(parent_component.name)
            data[parent_component.id]["features"].append({"name": feature.name, "type": feature.objectType})
        elif hasattr(
            entity, "sourceComponent"
        ):  # This is an occurrence - Reasons for an occurence - 1. creation of a component - 2. reference of a component (copy and paste) - 3. reference of a component (linked)
            occurrence = adsk.fusion.Occurrence.cast(entity)

            print_fusion(occurrence.sourceComponent.name)
            # This is for the creation of a component
            if occurrence.component.id not in data:
                parent_path = data[occurrence.sourceComponent.id]["path"]

                data[occurrence.component.id] = {
                    "path": os.path.join(parent_path, get_component_name(occurrence)),
                    "name": design.rootComponent.name,
                    "units": create_readable_value(
                        design.fusionUnitsManager.defaultLengthUnits,
                        cast(Literal[0, 1, 2, 3, 4], design.fusionUnitsManager.distanceDisplayUnits),
                    ),
                    "features": [],
                    "references": [],
                }
            else:
                parent_path = data[occurrence.sourceComponent.id]["path"]
                data[occurrence.component.id]["references"].append(
                    {"name": occurrence.name, "path": os.path.join(parent_path, get_component_name(occurrence))}
                )

            data[occurrence.sourceComponent.id]["features"].append(
                {"name": occurrence.name, "type": occurrence.objectType}
            )

    # Only the root component timeline has the json data
    # Though might wanna change it back to every file since makes sense for diffs
    # data["json"] = compress_json(data)
    return data


def get_component_timeline_data(doc=design) -> FusionComponentTimeline:
    component_timeline: FusionComponentTimeline = {doc.rootComponent.id: []}
    doc.attributes.add("CHURRO-EXPORT", doc.rootComponent.id, "")

    for timeline_item in doc.timeline:
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


def traverseAssembly(occurrences: adsk.fusion.OccurrenceList, path, component_timeline: FusionComponentTimeline):
    for occurrence in occurrences:
        try:
            # I check if component is not linked before adding occurrence.timelineObject.index since there seems to be an error in fusio
            # Also since a linked component will all reference the same component we're bing chilling - Since we need the index since the same level component
            # Could cause the folder to be overwritten as a reference - Which will never happen to a linked component since they all have the same folder
            folder_name = f"{occurrence.timelineObject.index if not occurrence.isReferencedComponent else ""}{occurrence.component.name}-{occurrence.component.id}"
            # ACTUALLY SCRATCH THAT - I'll Still need the index for linked components since they can be at the same level
            # Just don't need it for the respresentation in the linked_components folder
            occurrence_path = os.path.join(path, folder_name)
            original_component_occurence = root.allOccurrencesByComponent(occurrence.component).item(0)
            if occurrence == original_component_occurence:
                # This is the creation of the component
                write_component_data_to_file(occurrence, path, component_timeline)
            else:
                if (
                    not occurrence.isReferencedComponent
                ):  # Since if this is the second reference to a link it don't need to run cause it's in linked_components already
                    write_component_data_to_file(occurrence, path, component_timeline, True)

            # If it's a linked component we don't want to read further in for now
            if occurrence.childOccurrences and not occurrence.isReferencedComponent:
                traverseAssembly(occurrence.childOccurrences, occurrence_path, component_timeline)
        except Exception as e:
            error("Failed to traverse assembly", e)


def write_component_data_to_file(
    occurrence: adsk.fusion.Occurrence,
    folder_path: str,
    component_timeline: FusionComponentTimeline,
    component_reference=False,
):
    data: Timeline = {
        "document_name": occurrence.component.name,
        "units": create_readable_value(
            units_manager.defaultLengthUnits, cast(Literal[0, 1, 2, 3, 4], units_manager.distanceDisplayUnits)
        ),
        "features": [],
    }

    final_folder_path = os.path.join(src_folder_path, folder_path)

    # Regular component with features
    if not component_reference and not occurrence.isReferencedComponent:
        data["features"] = [
            get_timeline_feature(timeline_feature) for timeline_feature in component_timeline[occurrence.component.id]
        ]

    # Component reference
    # f"[{component_details['name']}]({component_details['path'].replace(' ', '%20').replace('\\', '/')}/timeline.md)"
    elif component_reference:
        data["info"] = {
            "link_to_component": f"[{occurrence.component.name}](/{os.path.join(output_folder, design.attributes.itemByName("CHURRO-EXPORT", occurrence.component.id).value, "timeline.md").replace(' ', '%20').replace('\\', '/')})",
            "component_reference": True,
            "component_reference_id": occurrence.component.id,
        }

    # Linked component
    elif occurrence.isReferencedComponent:
        data["info"] = {
            "link_to_component": f"[{occurrence.component.name}](/{os.path.join(output_folder, "linked_components", folder_path, "timeline.md").replace(' ', '%20').replace('\\', '/')})",
            "component_reference": False,
            "component_reference_id": occurrence.component.id,
        }
        # traverseAssembly(
        #     occurrence.childOccurrences,
        #     os.path.join(src_folder_path, "linked_components", os.path.basename(folder_path)),
        #     get_component_timeline_data(occurrence.component.parentDesign),
        # )
        # write_to_file(
        #     os.path.join(src_folder_path, "linked_components", os.path.basename(folder_path), "timeline.md"), data
        # )

    # write_to_file(os.path.join(final_folder_path, "timeline.md"), data)


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
