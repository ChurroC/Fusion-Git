
import adsk.fusion
from ..data_types import Sketch
from ..globals import print_fusion


def get_sketch_data(sketch: adsk.fusion.Sketch) -> Sketch:
    """Get detailed sketch data with error logging"""
    try:
        data: Sketch = {}

        # Get curves data with full geometry
        try:
            data["curves"] = []
            for curve in sketch.sketchCurves:
                curve_data = {
                    "type": curve.objectType,
                    "isConstruction": curve.isConstruction,
                }

                if isinstance(curve, adsk.fusion.SketchLine):
                    start_point = get_point_data(curve.startSketchPoint.geometry)
                    end_point = get_point_data(curve.endSketchPoint.geometry)
                    if start_point and end_point:
                        curve_data.update(
                            {
                                "startPoint": start_point,
                                "endPoint": end_point,
                                "constraints": [],
                            }
                        )
                        data["curves"].append(curve_data)

                elif isinstance(curve, adsk.fusion.SketchCircle):
                    center_point = get_point_data(curve.centerSketchPoint.geometry)
                    if center_point:
                        curve_data.update(
                            {
                                "centerPoint": center_point,
                                "radius": format_value(curve.radius),
                                "constraints": [],
                            }
                        )
                        data["curves"].append(curve_data)
        except Exception as e:
            print_fusion(f"Error processing curves: {str(e)}")

        # Get sketch plane data
        try:
            if sketch.referencePlane:
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
                plane: adsk.fusion.ConstructionPlane = sketch.referencePlane
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
            print_fusion(f"Error getting sketch plane: {str(e)}")

        return data

    except Exception as e:
        error_msg = f"Failed to get sketch details: {str(e)}\n{traceback.format_exc()}"
        print_fusion(error_msg)
        return {"error": error_msg}
