import adsk.fusion
from globals.utils import get_point_data, format_value
from globals.types.types import Error, ExtrudeDetails, OneSideExtent
from globals.globals import error


def get_extrude_data(extrude: adsk.fusion.ExtrudeFeature) -> ExtrudeDetails | Error:
    try:
        data: ExtrudeDetails = {
            "operation": extrude.operation,
            "extent": get_extent_data(extrude),
        }
        

    except Exception as e:
        error(e, "Failed to process extrudes")
    
    return data


def get_extent_data(extrude: adsk.fusion.ExtrudeFeature) -> dict:
    try:
        extent_type = extrude.extentType
        
        if extent_type == adsk.fusion.FeatureExtentTypes.OneSideFeatureExtentType:
            data: OneSideExtent = {
                "type": extent_type,
                "distance": {
                    "side_one": adsk.fusion.DistanceExtentDefinition.cast(extrude.extentOne).distance.expression
                }
            }
            return data
        
        
        extrude.extentOne
        extent = extrude.endFaces[0].body.extents
        extent_type = extent.extentType
        data = {}
        if extent_type == adsk.fusion.FeatureExtentTypes.OneSideFeatureExtentType:
            data = {
                "type": extent_type,
                "distance": {
                    "side_one": format_value(extent.distanceOne),
                    "side_two": None,
                    "symmetric": None
                }
            }
        elif extent_type == adsk.fusion.FeatureExtentTypes.TwoSidesFeatureExtentType:
            data = {
                "type": extent_type,
                "distance": {
                    "side_one": format_value(extent.distanceOne),
                    "side_two": format_value(extent.distanceTwo),
                    "symmetric": None
                }
            }
        elif extent_type == adsk.fusion.FeatureExtentTypes.SymmetricFeatureExtentType:
            data = {
                "type": extent_type,
                "distance": {
                    "side_one": None,
                    "side_two": None,
                    "symmetric": {
                        "value": format_value(extent.distanceOne),
                        "isFullLength": extent.isSymmetric
                    }
                }
            }
        return data
    except Exception as e:
        error(e, "Failed to process extrude extent data")
        return {}