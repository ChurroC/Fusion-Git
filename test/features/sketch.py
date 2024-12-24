import adsk.fusion
from ..globals.utils import get_point_data, format_value
from ..globals.types.types import SketchDetails, Error, Curve, LineCurve, CircleCurve, Plane
from ..globals.globals import error, root


def set_sketch_data(sketch: SketchDetails) -> None:
    try:
        plane = set_plane_data(sketch["details"]["plane"])
        sketch = root.sketches.add(plane)
        set_sketch_entities(sketch["details"]["curves"])
        ww = sketch["details"]

    except Exception as e:
        error("Failed to process sketches", e)

def set_plane_data(plane: Plane) -> adsk.fusion.ConstructionPlane | None:
    try:
        if (plane["type"] == "base_plane"): 
            if (plane["name"] == "XY"):
                return root.xYConstructionPlane
            elif (plane["name"] == "XZ"):
                return root.xZConstructionPlane
            elif (plane["name"] == "YZ"):
                return root.yZConstructionPlane
            else:
                return error("Unknown base plane")
        else:
            return error("Unknown plane type")
    except Exception as e:
        return error("Failed to process plane", e)

def set_sketch_entities(curves: Curve) -> None:
    try:
        for curve in curves:
            if curve["type"] == adsk.fusion.SketchCircle.classType():
                center = get_point_data(curve["centerPoint"])
                radius = units_manager.evaluateExpression(curve["radius"])
                if center and radius:
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)

            elif curve["type"] == adsk.fusion.SketchLine.classType():
                start = get_point_data(curve["startPoint"])
                end = get_point_data(curve["endPoint"])
                if start and end:
                    sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
        else:
            error("Unknown curve type")
    except Exception as e:
        error("Failed to process curves", e)
