#Author-
#Description-
# import nah
import adsk.core, adsk.fusion
from typing import cast
import json

from .globals.globals import ui, units_manager, active_document, error, print_fusion, is_error
from .globals.types.types import Timeline, Feature, Error

from .features.features import set_sketch_data, set_extrude_data

def run(context):
    try:
        fileDialog = ui.createFileDialog()
        fileDialog.title = "Select Timeline JSON File"
        fileDialog.filter = "JSON files (*.json)"

        if fileDialog.showOpen() != adsk.core.DialogResults.DialogOK:
            return

        timeline_data: Timeline
        with open(fileDialog.filename, "r") as f:
            timeline_data = json.load(f)
        
        active_document.name = timeline_data["document_name"]
        units_manager.distanceDisplayUnits = timeline_data["units"]
        
        for feature in timeline_data["features"]:
            set_feature_data(feature)
        
        print_fusion("Timeline successfully imported")
    except Exception as e:
        error("Failed to import timeline", e)

def set_feature_data(feature: Feature | Error) -> None:
    try:
        if is_error(feature):
            return error("Failed to process feature", feature)
        
        if feature["type"] == adsk.fusion.Sketch.classType():
            print_fusion(f"Processing sketch: {feature['name']}")
            set_sketch_data(feature)
        elif feature["type"] == adsk.fusion.ExtrudeFeature.classType():
            print_fusion(f"Processing extrude: {feature['name']}")
            set_extrude_data(feature)
        else:
            return error("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature", e)