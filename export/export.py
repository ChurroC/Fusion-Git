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
        folder_path = folderDialog.folder

        global component_timeline
        component_timeline = get_component_timeline_data()
        
        # This is just for dev purposes
        write_to_file(os.path.join(folder_path, 'component_timeline.json'), get_component_timeline_data(True))
        
        export_timeline_date(folder_path, component_timeline[design.rootComponent.id], design.rootComponent)
        
        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)

def get_component_timeline_data(readable = False) -> FusionComponentTimeline:
    component_timeline: FusionComponentTimeline = {}
    timeline = design.timeline
    for timeline_item in timeline:
        entity = timeline_item.entity
        component_id = None
        
        if hasattr(entity, 'parentComponent'):
            component_id = cast(adsk.fusion.Feature, entity).parentComponent.name if readable else cast(adsk.fusion.Feature, entity).parentComponent.id # If I try to cast using fusion api it deletes parentComponent for some reason
        elif hasattr(entity, 'sourceComponent'):
            occurrence = adsk.fusion.Occurrence.cast(entity)
            component_id = occurrence.sourceComponent.name if readable else occurrence.sourceComponent.id
            
        if component_id:
            if component_id not in component_timeline:
                component_timeline[component_id] = []
            component_timeline[component_id].append(timeline_item.name.strip() if readable else timeline_item)
    
    return component_timeline

def export_timeline_date(path: str, timeline: adsk.fusion.Timeline, root_component: adsk.fusion.Component):
    # The timline param is going through component_timeline so it's already filtered and has only the features of the target component
    data: Timeline = {
        "document_name": app.activeDocument.name,
        "units": units_manager.distanceDisplayUnits,
        "features": [],
    }
    
    for timeline_item in timeline:
        data["features"].append(get_timeline_feature(path, timeline_item, root_component))
    
    write_to_file(os.path.join(path, 'timeline.json'), data)

def get_timeline_feature(path: str, feature: adsk.fusion.TimelineObject, root_component: adsk.fusion.Component) -> Feature | Error:
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
            
            if not occurrence.isReferencedComponent:
                occurrences = root_component.occurrencesByComponent(component)
                if occurrences.item(0).name == occurrence.name: # If it's the first occurrence
                    global component_timeline
                    export_timeline_date(os.path.join(path, component.name), component_timeline[component.id], component)
            
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