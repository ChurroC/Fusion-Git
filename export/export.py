# Author - ChurroC
# Description - Export timeline data to a JSON file

import adsk.core, adsk.fusion
import os
import json

from .globals.globals import app, ui, units_manager, design, error, print_fusion
from .globals.types.types import Component, Feature, SketchFeature, ExtrudeFeature, Error

from .features.features import get_sketch_data, get_extrude_data

def run(context):
    try:
        folderDialog = ui.createFolderDialog()
        folderDialog.title = "Save Timeline Export"
        folderDialog.initialDirectory = "data" # Hmmm doesn't seem to wrok

        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        folder = folderDialog.folder

        data: Component = {
            "document_name": app.activeDocument.name,
            "units": units_manager.distanceDisplayUnits,
            "features": [],
        }

        timeline: adsk.fusion.Timeline = design.timeline
        for i in range(timeline.count):
            data["features"].append(get_timeline_data(timeline.item(i)))
        
        with open(os.path.join(folder, 'features.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print_fusion("Timeline successfully exported")
    except Exception as e:
        error("Failed to export timeline", e)

def get_timeline_data(feature: adsk.fusion.TimelineObject) -> Feature | Error:
    try:
        entity = feature.entity
        feature_type = entity.objectType
        index = feature.index
        print_fusion(feature_type)
        print_fusion(feature_type)
        
        if feature_type == adsk.fusion.Sketch.classType():
            entity = adsk.fusion.Sketch.cast(entity)
            sketch_feature_data: SketchFeature = {
                "name": entity.name,
                "type": feature_type,
                "index": index,
                "details": get_sketch_data(entity)
            }
            return sketch_feature_data
        elif feature_type == adsk.fusion.ExtrudeFeature.classType():
            entity = adsk.fusion.ExtrudeFeature.cast(entity)
            extrude_feature_data: ExtrudeFeature = {
                "name": entity.name,
                "type": feature_type,
                "index": index,
                "details": get_extrude_data(entity)
            }
            return extrude_feature_data
        elif feature_type == adsk.fusion.Occurrence.classType():
            entity = adsk.fusion.Occurrence.cast(entity)
            # print_fusion(feature_type)
            # print_fusion(str(entity.isVisible))
            # print_fusion(str(entity.isReferencedComponent))
            # print_fusion(str(entity.isReferencedComponent))
            # print_fusion(str(entity.isPatternElement))
            # print_fusion(feature_type)
        else:
            raise Exception("Unknown feature type")
    except Exception as e:
        return error("Failed to process feature", e)