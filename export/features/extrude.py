from typing import Literal, cast
import adsk.fusion
from ..globals.types.types import Error, ExtrudeExtent, ExtrudeDetails, OneSideExtent, TwoSidesExtent, SymmetricExtent
from ..globals.globals import error


def get_extrude_data(extrude: adsk.fusion.ExtrudeFeature) -> ExtrudeDetails | Error:
    try:
        data: ExtrudeDetails = {
            "operation": cast(Literal[0, 1, 2, 3, 4], extrude.operation),
            "extent": get_extent_data(extrude),
        }
        
        return data

    except Exception as e:
        return error(f"Failed to process extrudes {extrude.name}", e)


def get_extent_data(extrude: adsk.fusion.ExtrudeFeature) -> ExtrudeExtent | Error:
    extent_type = extrude.extentType
    
    if extent_type == adsk.fusion.FeatureExtentTypes.OneSideFeatureExtentType:
        one_side_data: OneSideExtent = {
            "type": cast(Literal[0], extent_type),
            "side_one": adsk.fusion.DistanceExtentDefinition.cast(extrude.extentOne).distance.expression
        }
        return one_side_data
    elif extent_type == adsk.fusion.FeatureExtentTypes.TwoSidesFeatureExtentType:
        two_side_data: TwoSidesExtent = {
            "type": cast(Literal[1], extent_type),
            "side_one": adsk.fusion.DistanceExtentDefinition.cast(extrude.extentOne).distance.expression,
            "side_two": adsk.fusion.DistanceExtentDefinition.cast(extrude.extentTwo).distance.expression
        }
        return two_side_data
    elif extent_type == adsk.fusion.FeatureExtentTypes.SymmetricFeatureExtentType:
        symetric_data: SymmetricExtent = {
            "type": cast(Literal[2], extent_type),
            "distance": adsk.fusion.ModelParameter.cast(extrude.symmetricExtent.distance).expression,
            "isFullLength": extrude.symmetricExtent.isFullLength
        }
        return symetric_data
    else:
        raise Exception("Unknown extent type")