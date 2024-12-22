import adsk.fusion
from globals.utils import get_point_data, format_value
from globals.types.types import Error, ExtrudeDetails, LineCurve, CircleCurve, PlaneFace, PlaneCustom, PlaneBase
from globals.globals import error


def get_extrude_data(sketch: adsk.fusion.ExtrudeFeature) -> ExtrudeDetails | Error:
    try:
        data: ExtrudeDetails = {
            "curves": [],
            "plane": get_plane_data(adsk.fusion.ConstructionPlane.cast(sketch.referencePlane))
        }
        
        for curve in sketch.sketchCurves:
            data["curves"].append(get_curve_data(curve))

    except Exception as e:
        error(e, "Failed to process extrudes")
    
    return data


def get_curve_data(curve: adsk.fusion.SketchCurve) -> LineCurve | CircleCurve | Error:
    try:
        curve_type = curve.objectType
        
        if curve_type == adsk.fusion.SketchLine.classType():
            curve = adsk.fusion.SketchLine.cast(curve)
            line_curve_data: LineCurve = {
                "type": curve_type,
                "startPoint": get_point_data(curve.startSketchPoint.geometry),
                "endPoint": get_point_data(curve.endSketchPoint.geometry),
            }
            return line_curve_data
        elif curve_type == adsk.fusion.SketchCircle.classType():
            curve = adsk.fusion.SketchCircle.cast(curve)
            circle_curve_data: CircleCurve = {
                "type": curve_type,
                "centerPoint": get_point_data(curve.centerSketchPoint.geometry),
                "radius": format_value(curve.radius),
            }
            return circle_curve_data
        else:
            error_info = "Unknown curve type"
            error_data: Error = {
                "error": error_info
            }
            error(error_info)
            return error_data
    except Exception as e:
        error_info = "Failed to process curves"
        error(e, error_info)
        error_data: Error = {
            "error": error_info
        }
        return error_data

def get_plane_data(plane: adsk.fusion.ConstructionPlane) -> PlaneFace | PlaneCustom | PlaneBase | Error:
    try:
        if (plane.objectType == adsk.fusion.BRepFace.classType()):
            # Sketch on surface
            face_plane_data: PlaneFace = {
                "type": "face",
            }
            return face_plane_data
        elif (plane.timelineObject is None):
            # Sketch on base planes - Like XY
            # We are going to stick with this for now till I get the main functionalities working
            base_plane_data: PlaneBase = {
                "type": "base_plane",
                "name": plane.name
            }
            return base_plane_data
        elif (plane.timelineObject is not None):
            # Sketch on custom planes"
            custom_plane_data: PlaneCustom = {
                "type": "custom_plane",
                "index": plane.timelineObject.index,
            }
            return custom_plane_data
        else:
            error_info = "Unknown plane type"
            error_data: Error = {
                "error": error_info
            }
            error(error_info)
            return error_data
    except Exception as e:
        error_info = "Failed to process plane"
        error(e, error_info)
        error_data: Error = {
            "error": error_info
        }
        return error_data