import adsk.core
import adsk.fusion
import traceback
import json
from datetime import datetime


def run(context):
    try:
        global app, ui, design, units_manager
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        units_manager = design.unitsManager

        fileDialog = ui.createFileDialog()
        fileDialog.title = "Save Timeline Export"
        fileDialog.filter = "JSON files (*.json)"
        fileDialog.initialFilename = "timeline_export.json"

        if fileDialog.showSave() != adsk.core.DialogResults.DialogOK:
            return

        success, message = export_timeline(fileDialog.filename)
        ui.messageBox(message)

    except:
        if ui:
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")


def format_value(value_input):
    """Format value using the design's default units"""
    try:
        return units_manager.formatInternalValue(
            value_input, units_manager.defaultLengthUnits, True
        )
    except:
        return str(value_input)


def get_point_data(point):
    """Get coordinates from a point"""
    try:
        return {
            "x": format_value(point.x),
            "y": format_value(point.y),
            "z": format_value(getattr(point, "z", 0)),
        }
    except Exception as e:
        print(f"Error getting point data: {str(e)}")
        return None


def get_sketch_data(sketch):
    """Get detailed sketch data with error logging"""
    try:
        data = {}

        # Basic sketch info
        try:
            data["profiles_count"] = sketch.profiles.count
            data["curves_count"] = sketch.sketchCurves.count

            # Get sketch plane data
            plane = sketch.referencePlane or sketch.constructionPlane
            if plane:
                data["plane"] = {
                    "origin": get_point_data(plane.origin),
                    "normal": get_point_data(plane.normal),
                    "xAxis": get_point_data(plane.xDirection),
                    "yAxis": get_point_data(plane.yDirection),
                }
        except Exception as e:
            print(f"Error getting basic sketch info: {str(e)}")

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
            print(f"Error processing curves: {str(e)}")

        # Get sketch plane data
        try:
            plane = sketch.referencePlane or sketch.constructionPlane
            if plane:
                data["plane"] = {
                    "origin": get_point_data(plane.origin),
                    "normal": get_point_data(plane.normal),
                }
        except Exception as e:
            print(f"Error getting sketch plane: {str(e)}")

        return data

    except Exception as e:
        error_msg = f"Failed to get sketch details: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {"error": error_msg}


def get_extrude_data(extrude):
    """Get detailed extrude data with error logging"""
    try:
        data = {}

        # Basic extrude info and operation type
        try:
            if hasattr(extrude, "operation"):
                data["operation"] = str(extrude.operation)

            if hasattr(extrude, "faces"):
                data["faces_count"] = extrude.faces.count
        except Exception as e:
            print(f"Error getting basic extrude info: {str(e)}")

        # Get extent details with full parameters
        try:
            if hasattr(extrude, "extentOne"):
                extent = extrude.extentOne
                if extent:
                    data["extent"] = {
                        "type": str(extent.extentType),
                        "distance": (
                            format_value(extent.distance.value)
                            if hasattr(extent, "distance")
                            else None
                        ),
                        "direction": (
                            get_point_data(extrude.direction)
                            if hasattr(extrude, "direction")
                            else None
                        ),
                    }
        except Exception as e:
            print(f"Error getting extrude extent: {str(e)}")

        # Get detailed profile information
        try:
            if hasattr(extrude, "profile"):
                profile = extrude.profile
                if profile:
                    # Get profile loops for complete geometry
                    profile_data = {"area": format_value(profile.area), "loops": []}

                    for loop in profile.profileLoops:
                        loop_data = {"isOuter": loop.isOuter, "vertices": []}

                        for vertex in loop.profileCurves:
                            # Get geometry for each curve in the profile
                            if hasattr(vertex, "geometry"):
                                if isinstance(vertex.geometry, adsk.core.Line3D):
                                    loop_data["vertices"].append(
                                        {
                                            "type": "line",
                                            "startPoint": get_point_data(
                                                vertex.geometry.startPoint
                                            ),
                                            "endPoint": get_point_data(
                                                vertex.geometry.endPoint
                                            ),
                                        }
                                    )
                                elif isinstance(vertex.geometry, adsk.core.Circle3D):
                                    loop_data["vertices"].append(
                                        {
                                            "type": "circle",
                                            "center": get_point_data(
                                                vertex.geometry.center
                                            ),
                                            "radius": format_value(
                                                vertex.geometry.radius
                                            ),
                                        }
                                    )

                        profile_data["loops"].append(loop_data)

                    data["profile"] = profile_data
        except Exception as e:
            print(f"Error getting profile info: {str(e)}")

        return data

    except Exception as e:
        error_msg = f"Failed to get extrude details: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {"error": error_msg}


def export_timeline(save_path):
    """Export timeline to JSON file with detailed error logging"""
    try:
        if not design:
            raise Exception("No active design")

        timeline = design.timeline

        export_data = {
            "documentName": app.activeDocument.name,
            "units": units_manager.defaultLengthUnits,
            "date": datetime.now().isoformat(),
            "featureCount": timeline.count,
            "features": [],
        }

        for i in range(timeline.count):
            try:
                feature = timeline.item(i)

                if not feature.entity:
                    print(f"No entity for feature {i + 1}")
                    continue

                entity = feature.entity
                feature_type = entity.classType()

                # Only process Sketch and Extrude features
                if (
                    "Sketch" not in feature_type
                    and "ExtrudeFeature" not in feature_type
                ):
                    continue

                feature_data = {
                    "index": i + 1,
                    "type": feature_type,
                    "name": entity.name,
                    "isRolledBack": feature.isRolledBack,
                }

                # Get feature-specific details
                if "Sketch" in feature_type:
                    print(f"Processing sketch: {entity.name}")
                    feature_data["details"] = get_sketch_data(entity)
                elif "ExtrudeFeature" in feature_type:
                    print(f"Processing extrude: {entity.name}")
                    feature_data["details"] = get_extrude_data(entity)

                export_data["features"].append(feature_data)

            except Exception as e:
                print(
                    f"Error processing feature {i + 1}: {str(e)}\n{traceback.format_exc()}"
                )
                continue

        # Write to JSON file
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        return True, "Timeline successfully exported"

    except Exception as e:
        return False, f"Failed to export timeline: {str(e)}\n{traceback.format_exc()}"


def stop(context):
    pass
