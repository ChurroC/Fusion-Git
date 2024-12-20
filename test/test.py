#Author-
#Description-
# import nah
import adsk.core, adsk.fusion
from typing import cast

from .globals import app, ui, units_manager, design, error, print_fusion
from .data_types import Timeline, Feature
from .features.sketch import get_sketch_data


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

                entity = feature.entity
                feature_type = entity.classType()
                
                feature_data: Feature
                # Only process Sketch and Extrude features
                if (feature_type == adsk.fusion.Sketch.classType()):
                    entity = adsk.fusion.Sketch.cast(entity)
                    print_fusion(f"Processing sketch: {entity.name}")
                    feature_data = {
                        "name": entity.name,
                        "type": feature_type,
                        "index": i + 1,
                        "details": get_sketch_data(entity)
                    }
                # elif (feature_type == adsk.fusion.ExtrudeFeature.classType()):
                #     entity = adsk.fusion.ExtrudeFeature.cast(entity)
                #     print_fusion(f"Processing extrude: {entity.name}")
                #     feature_data = {
                #         "name": entity.name,
                #         "type": feature_type,
                #         "index": i + 1,
                #         "details": get_extrude_data(entity)
                #     }
                else:
                    continue
                
                timeline_data["features"].append(feature_data)
            except Exception as e:
                error(e, "to process feature")
                continue

    except Exception as e:
        error(e, "to get timeline")
