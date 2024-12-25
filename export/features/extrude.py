import adsk.fusion
from ..globals.types.types import Error, ExtrudeExtent, ExtrudeDetails, OneSideExtent, TwoSidesExtent, SymmetricExtent
from ..globals.globals import error


def get_extrude_data(extrude: adsk.fusion.ExtrudeFeature) -> ExtrudeDetails | Error:
    try:
        data: ExtrudeDetails = {
            "operation": extrude.operation,
            "extent": get_extent_data(extrude),
        }
        
        return data

    except Exception as e:
        return error(f"Failed to process extrudes {extrude.name}", e)


def get_extent_data(extrude: adsk.fusion.ExtrudeFeature) -> ExtrudeExtent | Error:
    extent_type = extrude.extentType
    
    if extent_type == adsk.fusion.FeatureExtentTypes.OneSideFeatureExtentType:
        data: OneSideExtent = {
            "type": extent_type,
            "side_one": adsk.fusion.DistanceExtentDefinition.cast(extrude.extentOne).distance.expression
        }
        return data
    elif extent_type == adsk.fusion.FeatureExtentTypes.TwoSidesFeatureExtentType:
        data: TwoSidesExtent = {
            "type": extent_type,
            "side_one": adsk.fusion.DistanceExtentDefinition.cast(extrude.extentOne).distance.expression,
            "side_two": adsk.fusion.DistanceExtentDefinition.cast(extrude.extentTwo).distance.expression
        }
        return data
    elif extent_type == adsk.fusion.FeatureExtentTypes.SymmetricFeatureExtentType:
        data: SymmetricExtent = {
            "type": extent_type,
            "distance": adsk.fusion.ModelParameter.cast(extrude.symmetricExtent.distance).expression,
            "isFullLength": extrude.symmetricExtent.isFullLength
        }
        return data
    else:
        raise Exception("Unknown extent type")