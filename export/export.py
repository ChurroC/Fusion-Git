# Author - ChurroC
# Description - Export timeline data to a JSON file

from typing import cast
import adsk.core, adsk.fusion
import os

from .globals.globals import app, ui, units_manager, design, error, print_fusion
from .globals.types.types import Timeline, Feature, SketchFeature, ExtrudeFeature, Error, ComponentFeature, FusionComponentTimeline
from .globals.utils import write_to_file

from .features.features import get_sketch_data, get_extrude_data

component_timeline: FusionComponentTimeline

def run(context):
    try:
        folderDialog = ui.createFolderDialog()
        folderDialog.title = "Save Timeline Export"
        folderDialog.initialDirectory = "data" # Hmmm doesn't seem to wrok

        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        selected_folder_path = folderDialog.folder

        global component_timeline
        component_timeline = get_component_timeline_data()
        
        # This is just for dev purposes
        write_to_file(os.path.join(selected_folder_path, 'component_timeline.json'), get_component_timeline_data(True))
        
        
        for component_id in component_timeline:
            data: Timeline = {
                "document_name": app.activeDocument.name,
                "features": [],
            }
            if component_timeline[component_id]["is_linked"] or component_timeline[component_id]["is_root"]:
                data["units"] = units_manager.defaultLengthUnits
            
            folder_path = selected_folder_path
            if not component_timeline[component_id]["is_root"] and not component_timeline[component_id]["is_linked"]:
                folder_path = os.path.join(selected_folder_path, "components", component_timeline[component_id]["name"])
            elif component_timeline[component_id]["is_linked"]:
                folder_path = os.path.join(selected_folder_path, "linked_components", component_timeline[component_id]["name"])
            
            for timeline_item in component_timeline[component_id]["components"]:
                data["features"].append(get_timeline_feature(timeline_item))
            
            write_to_file(os.path.join(folder_path, 'timeline.json'), data)
        
        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)

def get_component_timeline_data(readable = False) -> FusionComponentTimeline:
    component_timeline: FusionComponentTimeline = {
        design.rootComponent.name if readable else design.rootComponent.id: {
            "is_root": True,
            "is_linked": False,
            "name": design.rootComponent.name,
            "components": []
        }
    }
    
    for timeline_item in design.timeline:
        entity = timeline_item.entity
        component_id = None
        
        if hasattr(entity, 'parentComponent'):
            parent_component = cast(adsk.fusion.Feature, entity).parentComponent # If I try to cast using fusion api it deletes parentComponent for some reason
            component_id = parent_component.name if readable else parent_component.id
        elif hasattr(entity, 'sourceComponent'):
            occurrence = adsk.fusion.Occurrence.cast(entity)
            source_component = occurrence.sourceComponent
            component_id = source_component.name if readable else source_component.id
            # This is when an occurance of a component occurs
            # We need to check if the component is already in our custom timeline
            component_timeline[occurrence.component.name if readable else occurrence.component.id] = {
                "is_root": False,
                "is_linked": occurrence.isReferencedComponent,
                "name": occurrence.component.name,
                "components": []
            }
        
        if component_id:
            component_timeline[component_id]["components"].append(timeline_item.name.strip() if readable else timeline_item)

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
                "type": feature_type,
                "details": get_sketch_data(extrude)
            }
            return sketch_feature_data
        elif feature_type == adsk.fusion.ExtrudeFeature.classType():
            sketch = adsk.fusion.ExtrudeFeature.cast(entity)
            extrude_feature_data: ExtrudeFeature = {
                "name": sketch.name,
                "type": feature_type,
                "details": get_extrude_data(sketch)
            }
            return extrude_feature_data
        elif feature_type == adsk.fusion.Occurrence.classType():
            occurrence = adsk.fusion.Occurrence.cast(entity)
            component = occurrence.component
            component_feature_data: ComponentFeature = {
                "name": component.name,
                "type": feature_type,
                "details": {
                    "is_linked": occurrence.isReferencedComponent,
                    "id": component.id
                }
            }
            return component_feature_data
        else:
            raise Exception("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature", e)