#Author-
#Description-
# import nah
from .globals import app, print_fusion, ui, units_manager, design, error
from .data_types import Timeline, Feature
import adsk.core, adsk.fusion
from typing import cast


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
            try:
                feature = timeline.item(i)

                if not feature.entity:
                    print_fusion(f"No entity for feature {i + 1}")
                    continue
                
                
                entity = adsk.fusion.Feature.cast(feature.entity)
                feature_type = entity.classType()
                
                # Only process Sketch and Extrude features
                if (
                    "Sketch" != feature_type
                    and "ExtrudeFeature" != feature_type
                ):
                    continue
                
                feature_data: Feature = {
                    "name": entity.name,
                    "type": feature_type,
                    "index": i + 1,
                }
                
                # Get feature-specific details
                if "Sketch" in feature_type:
                    print_fusion(f"Processing sketch: {entity.name}")
                    feature_data["details"] = get_sketch_data(entity)
                elif "ExtrudeFeature" in feature_type:
                    print_fusion(f"Processing extrude: {entity.name}")
                    feature_data["details"] = get_extrude_data(entity)
                
                timeline_data["features"].append(feature_data)
                
            except Exception as e:
                error(e, "to get timeline")
                continue

    except Exception as e:
        error(e, "to get timeline")
