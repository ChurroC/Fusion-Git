import adsk.fusion
from ..globals.utils import get_point_data, format_value
from ..globals.types.types import Error, SketchDetails, LineCurve, CircleCurve
from ..globals.globals import error


def get_sketch_data(sketch: adsk.fusion.Sketch) -> SketchDetails | Error:
    data: SketchDetails = {
        "curves": [],
    }
    
    for curve in sketch.sketchCurves:
        data["curves"].append(get_curve_data(curve))
        
    try:
        plane = adsk.fusion.ConstructionPlane.cast(sketch.referencePlane)
        """
        These are all the ideas for planes
        3 ways to creates sketches:
            1. Base contruction plane - XY or YZ Plane
                - Ideas is to use plane.name which return XY or YZ as plane name
            2. Create a plane object
                - When we support plane construction we could have plane.timelineObject
                    give us info on which plane in the timeline it is or use the plane name
            3. We create a sketch on the body of an extrude
                - This one gives us a BRepFace which we can recognize using plane.objectType
        """
        if (plane.objectType == adsk.fusion.BRepFace.classType()):
            # Sketch on surface
            data["plane"] = {
                "type": "face"
            }
        elif (plane.timelineObject is None):
            # Sketch on base planes - Like XY
            # We are going to stick with this for now till I get the main functionalities working
            data["plane"] = {
                "type": "base_plane",
                "name": plane.name
            }
        else:
            # Sketch on custom planes"
            data["plane"] = {
                "type": "custom_plane",
                "index": plane.timelineObject.index,
            }
    except Exception as e:
        error(e, "to process sketches")
    
    return data


def get_curve_data(curve: adsk.fusion.SketchCurve) -> LineCurve | CircleCurve | Error:
    try:
        curve_type = curve.objectType
        
        if curve_type == adsk.fusion.SketchLine.classType():
            curve = adsk.fusion.SketchLine.cast(curve)
            curve_data: LineCurve = {
                "type": curve_type,
                "startPoint": get_point_data(curve.startSketchPoint.geometry),
                "endPoint": get_point_data(curve.endSketchPoint.geometry),
            }
            return curve_data
        elif curve_type == adsk.fusion.SketchCircle.classType():
            curve = adsk.fusion.SketchCircle.cast(curve)
            curve_data: CircleCurve = {
                "type": curve_type,
                "centerPoint": get_point_data(curve.centerSketchPoint.geometry),
                "radius": format_value(curve.radius),
            }
            return curve_data
        else:
            error_data: Error = {
                "error": "Unknown curve type"
            }
            return error_data
    except Exception as e:
        error_info = "to process curves"
        error(e, error_info)
        error_data: Error = {
            "error": error_info
        }
        return error_data

def get_extrude_data(extrude: adsk.fusion.ExtrudeFeature):
    data = {
        "name": extrude.name,
        "type": "adsk::fusion::Extrude",
        "index": extrude.timelineObject.index,
        "details": get_sketch_data(extrude.profile.parentSketch)
    }
    return data