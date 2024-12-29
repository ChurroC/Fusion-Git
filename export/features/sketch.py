from typing import Literal, cast
import adsk.fusion
from ..globals.utils import get_point_data, format_value
from ..globals.types import (
    Error,
    SketchDetails,
    Curve,
    LineCurve,
    CircleCurve,
    Plane,
    PlaneFace,
    PlaneCustom,
    PlaneBase,
)
from ..globals.globals import error


def get_sketch_data(sketch: adsk.fusion.Sketch) -> SketchDetails | Error:
    try:
        data: SketchDetails = {
            "curves": [],
            "plane": get_plane_data(adsk.fusion.ConstructionPlane.cast(sketch.referencePlane)),
        }

        for curve in sketch.sketchCurves:
            data["curves"].append(get_curve_data(curve))

        return data

    except Exception as e:
        return error(f"Failed to process sketch {sketch.name}", e)


def get_curve_data(curve: adsk.fusion.SketchCurve) -> Curve | Error:
    curve_type = curve.objectType

    if curve_type == adsk.fusion.SketchLine.classType():
        curve = adsk.fusion.SketchLine.cast(curve)
        line_curve_data: LineCurve = {
            "type": cast(Literal["adsk::fusion::SketchLine"], curve_type),
            "start_point": get_point_data(curve.startSketchPoint.geometry),
            "end_point": get_point_data(curve.endSketchPoint.geometry),
        }
        return line_curve_data
    elif curve_type == adsk.fusion.SketchCircle.classType():
        curve = adsk.fusion.SketchCircle.cast(curve)
        circle_curve_data: CircleCurve = {
            "type": cast(Literal["adsk::fusion::SketchCircle"], curve_type),
            "center_point": get_point_data(curve.centerSketchPoint.geometry),
            "radius": format_value(curve.radius),
        }
        return circle_curve_data
    else:
        raise Exception("Unknown curve type")


def get_plane_data(plane: adsk.fusion.ConstructionPlane) -> Plane | Error:
    if plane.objectType == adsk.fusion.BRepFace.classType():
        # Sketch on surface
        face_plane_data: PlaneFace = {"type": "face"}
        return face_plane_data
    elif plane.timelineObject is None:
        # Sketch on base planes - Like XY
        # We are going to stick with this for now till I get the main functionalities working
        base_plane_data: PlaneBase = {"type": "base_plane", "name": plane.name}
        return base_plane_data
    elif plane.timelineObject is not None:
        # Sketch on custom planes"
        custom_plane_data: PlaneCustom = {
            "type": "custom_plane",
            "index": plane.timelineObject.index,
        }
        return custom_plane_data
    else:
        raise Exception("Unknown plane type")
