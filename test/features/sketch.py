import adsk.fusion
from ..globals.utils import get_point_data, format_value
from ..globals.data_types.features.sketch import SketchDetails, LineCurve, CircleCurve
from ..globals.data_types.timeline import Error
from ..globals.globals import error


def get_sketch_data(sketch: adsk.fusion.Sketch) -> SketchDetails | Error:
    data: SketchDetails = {
        "curves": [],
    }
    
    try:
        
        for curve in sketch.sketchCurves:
            curve_type = curve.objectType
            
            if curve_type == adsk.fusion.SketchLine.classType():
                curve = adsk.fusion.SketchLine.cast(curve)
                curve_data: LineCurve = {
                    "type": "adsk::fusion::SketchLine",
                    "startPoint": get_point_data(curve.startSketchPoint.geometry),
                    "endPoint": get_point_data(curve.endSketchPoint.geometry),
                }
                data["curves"].append(curve_data)
            elif curve_type == adsk.fusion.SketchCircle.classType():
                curve = adsk.fusion.SketchCircle.cast(curve)
                curve_data: CircleCurve = {
                    "type": "adsk::fusion::SketchCircle",
                    "centerPoint": get_point_data(curve.centerSketchPoint.geometry),
                    "radius": format_value(curve.radius),
                }
                data["curves"].append(curve_data)
    except Exception as e:
        error(e, "to process curves")
        
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
                "index": plane.timelineObject.index
            }
    except Exception as e:
        error(e, "to process sketches")
    
    return data