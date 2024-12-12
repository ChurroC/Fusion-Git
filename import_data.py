import adsk.core
import adsk.fusion
import traceback
import json


def run(context):
    try:
        global app, ui, design, units_manager, message
        message = ""
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        units_manager = adsk.fusion.FusionUnitsManager.cast(design.unitsManager)

        fileDialog = ui.createFileDialog()
        fileDialog.title = "Save Timeline Export"
        fileDialog.filter = "JSON files (*.json)"
        fileDialog.initialFilename = "timeline_export.json"

        if fileDialog.showSave() != adsk.core.DialogResults.DialogOK:
            return

        success = export_timeline(fileDialog.filename)

        ui.messageBox(str(success))
        ui.messageBox(message)
    except:
        if ui:
            print_fusion(f"Failed:\n{traceback.format_exc()}")


def print_fusion(new_print: str):
    global message
    # ui.messageBox(new_print)
    message += f"{new_print}\n"


def format_value(value_input):
    """Format value using the design's default units"""
    try:
        return units_manager.formatValue(value_input)
    except:
        return str(value_input)


def get_point_data(point: adsk.core.Point3D):
    """Get coordinates from a point"""
    try:
        return {
            "x": format_value(point.x),
            "y": format_value(point.y),
            "z": format_value(getattr(point, "z", 0)),
        }
    except Exception as e:
        print_fusion(f"Error getting point data: {str(e)}")
        return None


def remove_nulls(data):
    """Recursively removes null values from nested dictionaries and arrays."""
    if isinstance(data, dict):
        return {k: remove_nulls(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_nulls(item) for item in data if item is not None]
    else:
        return data


def get_sketch_data(sketch: adsk.fusion.Sketch):
    """Get detailed sketch data with error logging"""
    try:
        data = {}

        # Basic sketch info
        try:
            data["profiles_count"] = sketch.profiles.count
            data["curves_count"] = sketch.sketchCurves.count
        except Exception as e:
            print_fusion(f"Error getting basic sketch info: {str(e)}")

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
                plane: adsk.fusion.ConstructionPlane = sketch.referencePlane
                # This is a contruction plane type
                geo = plane.geometry
                # Then plane.geometry returns Plane object
                # normal, uVector, and vVector axis are 3d vectors
                data["plane"] = {
                    "origin": get_point_data(geo.origin),
                    "normal": {
                        "x": format_value(geo.normal.x),
                        "y": format_value(geo.normal.y),
                        "z": format_value(geo.normal.z),
                    },
                    "uVector": {
                        "x": format_value(geo.uDirection.x),
                        "y": format_value(geo.uDirection.y),
                        "z": format_value(geo.uDirection.z),
                    },
                    "vVector": {
                        "x": format_value(geo.vDirection.x),
                        "y": format_value(geo.vDirection.y),
                        "z": format_value(geo.vDirection.z),
                    },
                }
        except Exception as e:
            print_fusion(f"Error getting sketch plane: {str(e)}")

        return data

    except Exception as e:
        error_msg = f"Failed to get sketch details: {str(e)}\n{traceback.format_exc()}"
        print_fusion(error_msg)
        return {"error": error_msg}


def get_extrude_data(extrude: adsk.fusion.ExtrudeFeature):
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
            print_fusion(f"Error getting basic extrude info: {str(e)}")

        # Get extent details with full parameters
        try:
            print_fusion(str("to tweak or not to tweak"))

            data["extent"] = {
                "type": {
                    "value": int(extrude.extentType),
                    "name": {
                        adsk.fusion.FeatureExtentTypes.OneSideFeatureExtentType: "OneSideFeatureExtentType",
                        adsk.fusion.FeatureExtentTypes.TwoSidesFeatureExtentType: "TwoSidesFeatureExtentType",
                        adsk.fusion.FeatureExtentTypes.SymmetricFeatureExtentType: "SymmetricFeatureExtentType",
                    }[extrude.extentType],
                },
                "distance": {
                    "side_one": (
                        format_value(
                            adsk.fusion.DistanceExtentDefinition.cast(
                                extrude.extentOne
                            ).distance.value
                        )
                        if extrude.extentType == 0
                        else None
                    ),
                    "side_two": (
                        format_value(
                            adsk.fusion.DistanceExtentDefinition.cast(
                                extrude.extentTwo
                            ).distance.value
                        )
                        if extrude.extentType == 1
                        else None
                    ),
                    "symmetric": (
                        {
                            "value": (
                                format_value(
                                    adsk.fusion.ModelParameter.cast(
                                        extrude.symmetricExtent.distance
                                    ).value
                                )
                            ),
                            "isFullLength": extrude.symmetricExtent.isFullLength,
                        }
                        if extrude.extentType == 2
                        else None
                    ),
                },
            }
        except Exception as e:
            print_fusion(f"Error getting extrude extent: {str(e)}")

        # Get detailed profile information
        try:
            if hasattr(extrude, "profile"):
                profile_input = extrude.profile
                if profile_input:
                    data["profile_type"] = profile_input.classType()

                    if isinstance(profile_input, adsk.fusion.Profile):
                        # Single profile case
                        data["profile"] = {
                            "type": "profile",
                            "data": get_single_profile_data(profile_input),
                        }
                    elif isinstance(profile_input, adsk.fusion.BRepFace):
                        # Single planar face case
                        data["profile"] = {
                            "type": "planar_face",
                            "geometry": get_face_geometry(profile_input),
                        }
                    elif isinstance(profile_input, adsk.core.ObjectCollection):
                        # Collection of profiles/faces
                        data["profile"] = {"type": "collection", "items": []}
                        for i in range(profile_input.count):
                            item = profile_input.item(i)
                            if isinstance(item, adsk.fusion.Profile):
                                data["profile"]["items"].append(
                                    {
                                        "type": "profile",
                                        "data": get_single_profile_data(item),
                                    }
                                )
                            elif isinstance(item, adsk.fusion.BRepFace):
                                data["profile"]["items"].append(
                                    {
                                        "type": "planar_face",
                                        "data": get_face_geometry(item),
                                    }
                                )
        except Exception as e:
            print_fusion(f"Error getting profile info: {str(e)}")

        return data

    except Exception as e:
        error_msg = f"Failed to get extrude details: {str(e)}\n{traceback.format_exc()}"
        print_fusion(error_msg)
        return {"error": error_msg}


def get_single_profile_data(profile: adsk.fusion.Profile):
    """Process a single profile"""
    profile_data = {"area": format_value(profile.areaProperties()), "loops": []}

    for loop in profile.profileLoops:
        loop_data = {"isOuter": loop.isOuter, "vertices": []}

        for curve in loop.profileCurves:
            if hasattr(curve, "geometry"):
                if isinstance(curve.geometry, adsk.core.Line3D):
                    loop_data["vertices"].append(
                        {
                            "type": "line",
                            "startPoint": get_point_data(curve.geometry.startPoint),
                            "endPoint": get_point_data(curve.geometry.endPoint),
                        }
                    )
                elif isinstance(curve.geometry, adsk.core.Circle3D):
                    loop_data["vertices"].append(
                        {
                            "type": "circle",
                            "center": get_point_data(curve.geometry.center),
                            "radius": format_value(curve.geometry.radius),
                        }
                    )

        profile_data["loops"].append(loop_data)

    return profile_data


def get_face_geometry(face: adsk.fusion.BRepFace):
    """Get geometric data from a planar face"""
    try:
        surface = face.geometry
        surface_type = surface.surfaceType

        base_data = {
            "area": format_value(face.area),
            "surface": {
                "type": surface_type,
            },
        }

        # Handle different surface types
        if surface_type == adsk.core.SurfaceTypes.PlaneSurfaceType:
            surface = adsk.core.Plane.cast(surface)
            base_data["surface"].update(
                {
                    "origin": get_point_data(surface.origin),
                    "normal": {
                        "x": format_value(surface.normal.x),
                        "y": format_value(surface.normal.y),
                        "z": format_value(surface.normal.z),
                    },
                    "uVector": {
                        "x": format_value(surface.uDirection.x),
                        "y": format_value(surface.uDirection.y),
                        "z": format_value(surface.uDirection.z),
                    },
                    "vVector": {
                        "x": format_value(surface.vDirection.x),
                        "y": format_value(surface.vDirection.y),
                        "z": format_value(surface.vDirection.z),
                    },
                }
            )
        elif surface_type == adsk.core.SurfaceTypes.CylinderSurfaceType:
            surface = adsk.core.Cylinder.cast(surface)
            base_data["surface"].update(
                {
                    "origin": get_point_data(surface.origin),
                    "axis": {
                        "x": format_value(surface.axis.x),
                        "y": format_value(surface.axis.y),
                        "z": format_value(surface.axis.z),
                    },
                    "radius": format_value(surface.radius),
                }
            )
        elif surface_type == adsk.core.SurfaceTypes.ConeSurfaceType:
            surface = adsk.core.Cone.cast(surface)
            base_data["surface"].update(
                {
                    "origin": get_point_data(surface.origin),
                    "axis": {
                        "x": format_value(surface.axis.x),
                        "y": format_value(surface.axis.y),
                        "z": format_value(surface.axis.z),
                    },
                    "radius": format_value(surface.radius),
                    "halfAngle": format_value(surface.halfAngle),
                }
            )
        elif surface_type == adsk.core.SurfaceTypes.SphereSurfaceType:
            surface = adsk.core.Sphere.cast(surface)
            base_data["surface"].update(
                {
                    "origin": get_point_data(surface.origin),
                    "radius": format_value(surface.radius),
                }
            )
        elif surface_type == adsk.core.SurfaceTypes.TorusSurfaceType:
            surface = adsk.core.Torus.cast(surface)
            base_data["surface"].update(
                {
                    "origin": get_point_data(surface.origin),
                    "axis": {
                        "x": format_value(surface.axis.x),
                        "y": format_value(surface.axis.y),
                        "z": format_value(surface.axis.z),
                    },
                    "majorRadius": format_value(surface.majorRadius),
                    "minorRadius": format_value(surface.minorRadius),
                }
            )

        # Get edge geometry
        base_data["edges"] = [
            {
                "type": edge.geometry.curveType,
                "startPoint": get_point_data(edge.startVertex.geometry),
                "endPoint": get_point_data(edge.endVertex.geometry),
            }
            for edge in face.edges
        ]

        return base_data

    except Exception as e:
        print_fusion(f"Error getting face geometry: {str(e)}")
        return None


def export_timeline(save_path):
    """Export timeline to JSON file with detailed error logging"""
    try:
        if not design:
            raise Exception("No active design")

        timeline: adsk.fusion.Timeline = design.timeline

        export_data = {
            "documentName": app.activeDocument.name,
            "units": units_manager.defaultLengthUnits,
            "unitsEnum": units_manager.distanceDisplayUnits,
            "featureCount": timeline.count,
            "features": [],
        }

        for i in range(timeline.count):
            try:
                feature = timeline.item(i)

                if not feature.entity:
                    print_fusion(f"No entity for feature {i + 1}")
                    continue

                entity: adsk.fusion.Feature = feature.entity
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
                    print_fusion(f"Processing sketch: {entity.name}")
                    feature_data["details"] = get_sketch_data(entity)
                elif "ExtrudeFeature" in feature_type:
                    print_fusion(f"Processing extrude: {entity.name}")
                    feature_data["details"] = get_extrude_data(entity)

                export_data["features"].append(feature_data)

            except Exception as e:
                print_fusion(
                    f"Error processing feature {i + 1}: {str(e)}\n{traceback.format_exc()}"
                )
                continue

        # Write to JSON file
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
            # remove_nulls(export_data)

        print_fusion("Timeline successfully exported")
        return True

    except Exception as e:
        print_fusion(f"Failed to export timeline: {str(e)}\n{traceback.format_exc()}")
        return False
