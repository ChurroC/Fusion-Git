import adsk.fusion
from ..globals.utils import set_point_data
from ..globals.types.types import SketchDetails, Error, Curve, Plane
from ..globals.globals import error, root, units_manager


def set_sketch_data(sketch_details: SketchDetails | Error) -> None:
    try:
        if "error" in sketch_details:
            raise Exception("Failed to read sketch error data")
        
        plane = set_plane_data(sketch_details["plane"])
        set_sketch_entities(root.sketches.add(plane), sketch_details["curves"])

    except Exception as e:
        # maybe try to get name of sketch here
        error("Failed to process sketch", e)

def set_plane_data(plane: Plane | Error) -> adsk.fusion.ConstructionPlane:
    if "error" in plane:
        raise Exception("Failed to read plane error data")
    
    if (plane["type"] == "base_plane"): 
        if (plane["name"] == "XY"):
            return root.xYConstructionPlane
        elif (plane["name"] == "XZ"):
            return root.xZConstructionPlane
        elif (plane["name"] == "YZ"):
            return root.yZConstructionPlane
        else:
            raise Exception("Unknown base plane")
    else:
        raise Exception("Unknown plane type")

def set_sketch_entities(sketch: adsk.fusion.Sketch, curves: list[Curve | Error]):
    for curve in curves:
        if "error" in curve:
            raise Exception("Failed to read sketch curves error data")

        if curve["type"] == "adsk::fusion::SketchCircle": # adsk.fusion.SketchCircle.classType()
            center = set_point_data(curve["center_point"])
            radius = units_manager.evaluateExpression(curve["radius"])
            if center and radius:
                sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
        elif curve["type"] == "adsk::fusion::SketchLine": # adsk.fusion.SketchLine.classType()
            start = set_point_data(curve["start_point"])
            end = set_point_data(curve["end_point"])
            if start and end:
                sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
        else:
            raise Exception("Unknown curve type")
