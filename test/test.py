#Author-
#Description-
# import nah
import adsk.core, adsk.fusion
from typing import cast
import json

from .globals.globals import app, ui, units_manager, design, error, print_fusion
from .globals.types.types import Timeline, SketchFeature, ExtrudeFeature, Error

from .features.features import get_sketch_data

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
            "documentName": app.activeDocument.name,
            "units": cast(int, units_manager.distanceDisplayUnits),
            "features": [],
        }
        
        for i in range(timeline.count):
            timeline_data["features"].append(get_feature_data(timeline.item(i)))
        
        with open(fileDialog.filename, "w", encoding="utf-8") as f:
            json.dump(timeline_data, f, indent=2)

    except Exception as e:
        error("Failed to export timeline", e)

def get_feature_data(feature: adsk.fusion.TimelineObject) -> SketchFeature | ExtrudeFeature | Error:
    try:
        entity = feature.entity
        feature_type = entity.classType()
        
        if feature_type == adsk.fusion.Sketch.classType():
            entity = adsk.fusion.Sketch.cast(entity)
            print_fusion(f"Processing sketch: {entity.name}")
            feature_data: SketchFeature = {
                "name": entity.name,
                "type": feature_type,
                "details": get_sketch_data(entity)
            }
            return feature_data
        # elif (feature_type == adsk.fusion.ExtrudeFeature.classType()):
        #     entity = adsk.fusion.ExtrudeFeature.cast(entity)
        #     wow = entity.classType()
        #     print_fusion(f"Processing extrude: {entity.name}")
        #     feature_data: SketchFeature = {
        #         "name": entity.name,
        #         "type": entity.classType(),
        #         "details": get_sketch_data(entity)
        #     }
        #     return feature_data
        else:
            return error("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature")