import adsk.core
import adsk.fusion
import traceback
import os
from datetime import datetime


def format_value(value_input, units_manager):
    """Format value using the design's default units"""
    try:
        return units_manager.formatInternalValue(
            value_input, units_manager.defaultLengthUnits, True
        )
    except:
        return str(value_input)


def get_sketch_details(sketch, units_manager):
    """Get details about a sketch feature"""
    try:
        details = []
        details.append(f"Profiles count: {sketch.profiles.count}")
        details.append(f"Curves count: {sketch.sketchCurves.count}")

        # Count curve types
        curve_types = {"SketchLines": 0, "SketchCircles": 0, "SketchArcs": 0}

        # Get curve dimensions
        for curve in sketch.sketchCurves:
            if isinstance(curve, adsk.fusion.SketchLine):
                curve_types["SketchLines"] += 1
            elif isinstance(curve, adsk.fusion.SketchCircle):
                curve_types["SketchCircles"] += 1
            elif isinstance(curve, adsk.fusion.SketchArc):
                curve_types["SketchArcs"] += 1

        for curve_type, count in curve_types.items():
            if count > 0:
                details.append(f"{curve_type}: {count}")

        return details
    except Exception as e:
        return [f"Error getting sketch details: {str(e)}"]


def get_extrude_details(extrude, units_manager):
    """Get details about an extrude feature"""
    try:
        details = []

        # Get faces created by extrude
        if hasattr(extrude, "faces"):
            faces = extrude.faces
            details.append(f"Number of faces: {faces.count}")

        # Try to get extrude properties
        if hasattr(extrude, "extentOne"):
            extent = extrude.extentOne
            if extent and hasattr(extent, "distance"):
                distance = format_value(extent.distance.value, units_manager)
                details.append(f"Distance: {distance}")

        # Get operation type
        if hasattr(extrude, "operation"):
            operation_types = {
                adsk.fusion.FeatureOperations.CutFeatureOperation: "Cut",
                adsk.fusion.FeatureOperations.JoinFeatureOperation: "Join",
                adsk.fusion.FeatureOperations.IntersectFeatureOperation: "Intersect",
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation: "New Body",
            }
            operation = operation_types.get(extrude.operation, "Unknown")
            details.append(f"Operation: {operation}")

        return details
    except Exception as e:
        return [f"Error getting extrude details: {str(e)}"]


def get_revolve_details(revolve, units_manager):
    """Get details about a revolve feature"""
    try:
        details = []

        # Get angle if available
        if hasattr(revolve, "angle"):
            angle = format_value(revolve.angle.value, units_manager)
            details.append(f"Angle: {angle}")

        # Get operation type
        if hasattr(revolve, "operation"):
            operation_types = {
                adsk.fusion.FeatureOperations.CutFeatureOperation: "Cut",
                adsk.fusion.FeatureOperations.JoinFeatureOperation: "Join",
                adsk.fusion.FeatureOperations.IntersectFeatureOperation: "Intersect",
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation: "New Body",
            }
            operation = operation_types.get(revolve.operation, "Unknown")
            details.append(f"Operation: {operation}")

        return details
    except Exception as e:
        return [f"Error getting revolve details: {str(e)}"]


def get_primitive_details(primitive, units_manager):
    """Get details about primitive features (Box, Cylinder)"""
    try:
        details = []

        # For Box Feature
        if isinstance(primitive, adsk.fusion.BoxFeature):
            if hasattr(primitive, "length"):
                length = format_value(primitive.length.value, units_manager)
                details.append(f"Length: {length}")
            if hasattr(primitive, "width"):
                width = format_value(primitive.width.value, units_manager)
                details.append(f"Width: {width}")
            if hasattr(primitive, "height"):
                height = format_value(primitive.height.value, units_manager)
                details.append(f"Height: {height}")

        # For Cylinder Feature
        elif isinstance(primitive, adsk.fusion.CylinderFeature):
            if hasattr(primitive, "diameter"):
                diameter = format_value(primitive.diameter.value, units_manager)
                details.append(f"Diameter: {diameter}")
            if hasattr(primitive, "height"):
                height = format_value(primitive.height.value, units_manager)
                details.append(f"Height: {height}")

        return details
    except Exception as e:
        return [f"Error getting primitive details: {str(e)}"]


def export_timeline(save_path):
    """Export timeline to text file"""
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        units_manager = design.unitsManager

        if not design:
            raise Exception("No active design")

        timeline = design.timeline

        with open(save_path, "w", encoding="utf-8") as f:
            # Write header
            f.write(f"Fusion 360 Timeline Export\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Document: {app.activeDocument.name}\n")
            f.write(f"Default Units: {units_manager.defaultLengthUnits}\n")
            f.write(f"Total Features: {timeline.count}\n")
            f.write("-" * 50 + "\n\n")

            # Process each feature
            for i in range(timeline.count):
                try:
                    feature = timeline.item(i)
                    f.write(f"Feature {i + 1}:\n")

                    if feature.entity:
                        entity = feature.entity
                        feature_type = entity.classType()
                        f.write(f"Type: {feature_type}\n")
                        f.write(f"Name: {entity.name}\n")

                        # Get feature-specific details
                        if "Sketch" in feature_type:
                            details = get_sketch_details(entity, units_manager)
                        elif "ExtrudeFeature" in feature_type:
                            details = get_extrude_details(entity, units_manager)
                        elif "RevolveFeature" in feature_type:
                            details = get_revolve_details(entity, units_manager)
                        elif (
                            "BoxFeature" in feature_type
                            or "CylinderFeature" in feature_type
                        ):
                            details = get_primitive_details(entity, units_manager)
                        else:
                            details = []

                        if details:
                            f.write("Details:\n")
                            for detail in details:
                                f.write(f"  - {detail}\n")

                    f.write(
                        f"State: {'Rolled Back' if feature.isRolledBack else 'Active'}\n"
                    )
                    f.write("-" * 50 + "\n")

                except Exception as e:
                    f.write(f"Error processing feature {i + 1}: {str(e)}\n")
                    f.write("-" * 50 + "\n")
                    continue

        return True, "Timeline successfully exported"

    except:
        return False, f"Failed to export timeline:\n{traceback.format_exc()}"


def run(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        fileDialog = ui.createFileDialog()
        fileDialog.title = "Save Timeline Export"
        fileDialog.filter = "Text files (*.txt)"
        fileDialog.initialFilename = "timeline_export.txt"

        if fileDialog.showSave() != adsk.core.DialogResults.DialogOK:
            return

        success, message = export_timeline(fileDialog.filename)
        ui.messageBox(message)

    except:
        if ui:
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")


def stop(context):
    pass
