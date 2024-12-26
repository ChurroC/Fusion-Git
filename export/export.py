# Author - ChurroC
# Description - Export timeline data to a JSON file

import adsk.core, adsk.fusion
import os
import json

from .globals.globals import app, ui, units_manager, design, error, print_fusion
from .globals.types.types import Timeline, Feature, SketchFeature, ExtrudeFeature, Error, ComponentFeature

from .features.features import get_sketch_data, get_extrude_data

def run(context):
    try:
        folderDialog = ui.createFolderDialog()
        folderDialog.title = "Save Timeline Export"
        folderDialog.initialDirectory = "data" # Hmmm doesn't seem to wrok

        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        folder_path = folderDialog.folder

        
        get_timeline_data(folder_path, design.timeline, design.rootComponent, True)
        
        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)

def get_timeline_data(path: str, timeline: adsk.fusion.Timeline, root_component: adsk.fusion.Component, isRoot = False):
    data: Timeline = {
        "document_name": app.activeDocument.name,
        "units": units_manager.distanceDisplayUnits,
        "features": [],
    }
    
    for timeline_item in timeline:
        time_line_data = get_timeline_feature(path, timeline_item, root_component, isRoot)
        if time_line_data is not None:
            data["features"].append(time_line_data)
    
    file_path = os.path.join(path, 'features.json')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_timeline_feature(path: str, feature: adsk.fusion.TimelineObject, root_component: adsk.fusion.Component, isRoot = False) -> Feature | Error | None:
    try:
        entity = feature.entity
        feature_type = entity.objectType
        # index = feature.index
        print_fusion()
        print_fusion("This is root") if isRoot else ""
        print_fusion(feature_type)
        
        if feature_type == adsk.fusion.Sketch.classType():
            extrude = adsk.fusion.Sketch.cast(entity)
            if root_component.id != extrude.parentComponent.id:
                return None
            sketch_feature_data: SketchFeature = {
                "name": extrude.name,
                "type": feature_type,
                "details": get_sketch_data(extrude)
            }
            return sketch_feature_data
        elif feature_type == adsk.fusion.ExtrudeFeature.classType():
            sketch = adsk.fusion.ExtrudeFeature.cast(entity)
            if root_component.id != sketch.parentComponent.id:
                return None
            extrude_feature_data: ExtrudeFeature = {
                "name": sketch.name,
                "type": feature_type,
                "details": get_extrude_data(sketch)
            }
            return extrude_feature_data
        elif feature_type == adsk.fusion.Occurrence.classType():
            occurrence = adsk.fusion.Occurrence.cast(entity)
            # Check if occurrence is in root component
            if occurrence.sourceComponent.id != root_component.id:
                return None
            
            component = occurrence.component
            print_fusion(component.name)
            
            occurrences = root_component.occurrencesByComponent(component)
            is_first_occurrence = occurrences.item(0).name == occurrence.name
            
            print_fusion(is_first_occurrence)
            if is_first_occurrence:
                timeline = design.timeline
                component_features = []
                for timeline_item in timeline:
                    entity = timeline_item.entity
                    
                    # Check if this feature belongs to our component
                    if (hasattr(entity, 'parentComponent') and entity.parentComponent.id == component.id) or (hasattr(entity, 'sourceComponent') and entity.sourceComponent.id == component.id):
                        component_features.append(timeline_item)
                print_fusion(os.path.join(path, component.name))
                get_timeline_data(os.path.join(path, component.name), component_features, component)
            
            component_feature_data: ComponentFeature = {
                "name": occurrence.component.name,
                "type": feature_type,
                "details": {
                    "is_linked": occurrence.isReferencedComponent,
                    "id": occurrence.component.id
                }
            }
            return component_feature_data
        else:
            raise Exception("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature", e)