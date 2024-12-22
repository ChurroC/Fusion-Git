#Author-
#Description-
# import nah
import adsk.core, adsk.fusion
from typing import cast

from .globals.globals import app, ui, units_manager, design, error, print_fusion
from .globals.types.types import Timeline, SketchFeature, ExtrudeFeature, Error

from .features.features import get_sketch_data

def run(context):
    fileDialog = ui.createFileDialog()
    fileDialog.title = "Save Timeline Export"
    fileDialog.filter = "JSON files (*.json)"
    fileDialog.initialFilename = "timeline_export.json"

    if fileDialog.showSave() != adsk.core.DialogResults.DialogOK:
        return

    try:
        timeline: adsk.fusion.Timeline = design.timeline

        timeline_data: Timeline = {
            "documentName": app.activeDocument.name,
            "units": cast(int, units_manager.distanceDisplayUnits),
            "features": [],
        }
        
        for i in range(timeline.count):
            timeline_data["features"].append(get_feature_data(timeline.item(i)))

    except Exception as e:
        error(e, "Failed to process timeline")

def get_feature_data(feature: adsk.fusion.TimelineObject) -> SketchFeature | ExtrudeFeature | Error:
    try:
        entity = feature.entity
        index = feature.index
        feature_type = entity.classType()
        
        if feature_type == adsk.fusion.Sketch.classType():
            entity = adsk.fusion.Sketch.cast(entity)
            print_fusion(f"Processing sketch: {entity.name}")
            feature_data: SketchFeature = {
                "name": entity.name,
                "type": feature_type,
                "index": index,
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
        #         "index": i + 1,
        #         "details": get_sketch_data(entity)
        #     }
        #     return feature_data
        else:
            error_info = "Unknown feature type"
            error_data: Error = {
                "error": error_info
            }
            error(error_info)
            return error_data
    except Exception as e:
        error_info = "Failed to process feature"
        error(e, error_info)
        error_data: Error = {
            "error": error_info
        }
        return error_data