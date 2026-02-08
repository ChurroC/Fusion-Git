import adsk.fusion
from ..globals.utils import set_point_data
from ..globals.types import SketchDetails, Error, Curve, Plane
from ..globals.globals import error, root, units_manager


def set_sketch_data(sketch_details: SketchDetails | Error) -> None:
    try:
        if "error" in sketch_details:
            raise Exception("Failed to read sketch error data")

        plane = set_plane_data(sketch_details["plane"])
        sketch = root.sketches.add(plane)
        set_sketch_entities(sketch, sketch_details["curves"])

    except Exception as e:
        error("Failed to process sketch", e)


def set_plane_data(plane: Plane | Error) -> adsk.fusion.ConstructionPlane:
    if "error" in plane:
        raise Exception("Failed to read plane error data")

    plane_type = plane["type"]["value"]

    if plane_type == "base_plane":
        plane_name = plane["name"]

        if plane_name == "XY":
            return root.xYConstructionPlane
        elif plane_name == "XZ":
            return root.xZConstructionPlane
        elif plane_name == "YZ":
            return root.yZConstructionPlane
        else:
            raise Exception(f"Unknown base plane: {plane_name}")
    else:
        raise Exception(f"Plane type '{plane_type}' not yet supported, only base planes (XY/XZ/YZ)")


def set_sketch_entities(sketch: adsk.fusion.Sketch, curves: list[Curve | Error]) -> None:
    for index, curve in enumerate(curves):
        try:
            if "error" in curve:
                raise Exception("Failed to read sketch curve error data")

            curve_type = curve["type"]["value"]

            if curve_type == "adsk::fusion::SketchLine":
                set_sketch_line(sketch, curve)

            elif curve_type == "adsk::fusion::SketchCircle":
                set_sketch_circle(sketch, curve)

            else:
                continue

        except Exception as e:
            error(f"Failed to process curve {index} in sketch", e)


def set_sketch_line(sketch: adsk.fusion.Sketch, curve: Curve) -> None:
    """Create a sketch line"""
    start = set_point_data(curve["start_point"])
    end = set_point_data(curve["end_point"])

    if start and end:
        sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    else:
        raise Exception("Invalid line data: missing start or end point")


def set_sketch_circle(sketch: adsk.fusion.Sketch, curve: Curve) -> None:
    """Create a sketch circle"""
    center = set_point_data(curve["center_point"])
    radius = units_manager.evaluateExpression(curve["radius"])

    if center and radius:
        sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
    else:
        raise Exception("Invalid circle data: missing center or radius")
