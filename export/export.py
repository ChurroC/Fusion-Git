#Author-
#Description-
# import nah
import adsk.core, adsk.fusion
import json

from .globals.globals import app, ui, units_manager, design, error, print_fusion
from .globals.types.types import Timeline, Feature, SketchFeature, ExtrudeFeature, Error

from .features.features import get_sketch_data, get_extrude_data

def run(context):
    try:
        fileDialog = ui.createFileDialog()
        fileDialog.title = "Save Timeline Export"
        fileDialog.filter = "JSON files (*.json)"
        fileDialog.initialFilename = "timeline_export.json"

        if fileDialog.showSave() != adsk.core.DialogResults.DialogOK:
            return

        timeline: adsk.fusion.Timeline = design.timeline

        timeline_data: Timeline = {
            "document_name": app.activeDocument.name,
            "units": units_manager.distanceDisplayUnits,
            "features": [],
        }
        
        for i in range(timeline.count):
            timeline_data["features"].append(get_feature_data(timeline.item(i)))
        
        with open(fileDialog.filename, "w", encoding="utf-8") as f:
            json.dump(timeline_data, f, indent=2)
        
        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)

def get_feature_data(feature: adsk.fusion.TimelineObject) -> Feature | Error:
    try:
        entity = feature.entity
        feature_type = entity.classType()
        index = feature.index
        
        if feature_type == adsk.fusion.Sketch.classType():
            entity = adsk.fusion.Sketch.cast(entity)
            print_fusion(f"Processing sketch: {entity.name}")
            sketch_feature_data: SketchFeature = {
                "name": entity.name,
                "type": feature_type,
                "index": index,
                "details": get_sketch_data(entity)
            }
            return sketch_feature_data
        elif feature_type == adsk.fusion.ExtrudeFeature.classType():
            entity = adsk.fusion.ExtrudeFeature.cast(entity)
            print_fusion(f"Processing extrude: {entity.name}")
            extrude_feature_data: ExtrudeFeature = {
                "name": entity.name,
                "type": feature_type,
                "index": index,
                "details": get_extrude_data(entity)
            }
            return extrude_feature_data
        else:
            raise Exception("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature", e)