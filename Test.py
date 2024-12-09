import adsk.core
import adsk.fusion
import traceback
import os
from datetime import datetime


def convert_to_inch(value, from_unit):
    """Convert any unit to inches"""
    try:
        # If the value is already in inches, return it
        if from_unit == "in":
            return round(value, 3)

        # Convert from centimeters to inches
        if from_unit == "cm":
            return round(value / 2.54, 3)

        # Convert from millimeters to inches
        if from_unit == "mm":
            return round(value / 25.4, 3)

        # For any other unit, try using the units manager
        units_manager = adsk.core.Application.get().activeProduct.unitsManager
        return round(units_manager.convert(value, from_unit, "in"), 3)
    except:
        return value


def format_measurement(value, unit="in"):
    """Format a measurement value with unit"""
    try:
        return f"{round(float(value), 3)} {unit}"
    except:
        return f"{value} {unit}"


def get_sketch_details(sketch):
    """Get details about a sketch feature"""
    try:
        details = []
        details.append(f"Profiles count: {sketch.profiles.count}")
        details.append(f"Curves count: {sketch.sketchCurves.count}")

        # Get sketch curves details
        curve_types = {"SketchLines": 0, "SketchCircles": 0, "SketchArcs": 0}

        # Get curve dimensions
        total_length = 0
        for curve in sketch.sketchCurves:
            if isinstance(curve, adsk.fusion.SketchLine):
                curve_types["SketchLines"] += 1
                total_length += curve.length
            elif isinstance(curve, adsk.fusion.SketchCircle):
                curve_types["SketchCircles"] += 1
                total_length += curve.length
            elif isinstance(curve, adsk.fusion.SketchArc):
                curve_types["SketchArcs"] += 1
                total_length += curve.length

        for curve_type, count in curve_types.items():
            if count > 0:
                details.append(f"{curve_type}: {count}")

        if total_length > 0:
            length_in_inches = convert_to_inch(total_length, "cm")
            details.append(
                f"Total curve length: {format_measurement(length_in_inches)}"
            )

        return details
    except Exception as e:
        return [f"Error getting sketch details: {str(e)}"]


def get_extrude_details(extrude):
    """Get details about an extrude feature"""
    app = adsk.core.Application.get()
    ui = app.userInterface
    ui.messageBox("distance_in_inches")
    try:
        details = []

        # Get faces created by extrude
        if hasattr(extrude, "faces"):
            faces = extrude.faces
            details.append(f"Number of faces: {faces.count}")

        # Try to get extrude properties
        if hasattr(extrude, "extentOne"):
            ui.messageBox("distance_in_inches1")
            extent = extrude.extentOne
            if extent and hasattr(extent, "distance"):
                ui.messageBox("distance_in_inches2")
                # Get the value in the current unit system
                distance_value = extent.distance.value
                distance_unit = extent.distance.unit
                distance_in_inches = convert_to_inch(distance_value, distance_unit)
                ui.messageBox("distance_in_inches3")
                ui.messageBox(distance_in_inches)
                details.append(
                    f"Distance: {format_measurement(distance_in_inches)} (Original: {distance_value} {distance_unit})"
                )

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


def get_revolve_details(revolve):
    """Get details about a revolve feature"""
    try:
        details = []

        # Get angle if available
        if hasattr(revolve, "angle"):
            angle_value = revolve.angle.value
            details.append(f"Angle: {format_measurement(angle_value, 'deg')}")

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


def get_primitive_details(primitive):
    """Get details about primitive features (Box, Cylinder)"""
    try:
        details = []

        # For Box Feature
        if isinstance(primitive, adsk.fusion.BoxFeature):
            if hasattr(primitive, "length"):
                length_in_inches = convert_to_inch(
                    primitive.length.value, primitive.length.unit
                )
                details.append(f"Length: {format_measurement(length_in_inches)}")
            if hasattr(primitive, "width"):
                width_in_inches = convert_to_inch(
                    primitive.width.value, primitive.width.unit
                )
                details.append(f"Width: {format_measurement(width_in_inches)}")
            if hasattr(primitive, "height"):
                height_in_inches = convert_to_inch(
                    primitive.height.value, primitive.height.unit
                )
                details.append(f"Height: {format_measurement(height_in_inches)}")

        # For Cylinder Feature
        elif isinstance(primitive, adsk.fusion.CylinderFeature):
            if hasattr(primitive, "diameter"):
                diameter_in_inches = convert_to_inch(
                    primitive.diameter.value, primitive.diameter.unit
                )
                details.append(f"Diameter: {format_measurement(diameter_in_inches)}")
            if hasattr(primitive, "height"):
                height_in_inches = convert_to_inch(
                    primitive.height.value, primitive.height.unit
                )
                details.append(f"Height: {format_measurement(height_in_inches)}")

        return details
    except Exception as e:
        return [f"Error getting primitive details: {str(e)}"]


def export_timeline(save_path):
    """Export timeline to text file"""
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct

        if not design:
            raise Exception("No active design")

        timeline = design.timeline

        with open(save_path, "w", encoding="utf-8") as f:
            # Write header
            f.write(f"Fusion 360 Timeline Export\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Document: {app.activeDocument.name}\n")
            f.write(f"Units: Inches\n")
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
                            details = get_sketch_details(entity)
                        elif "ExtrudeFeature" in feature_type:
                            details = get_extrude_details(entity)
                        elif "RevolveFeature" in feature_type:
                            details = get_revolve_details(entity)
                        elif (
                            "BoxFeature" in feature_type
                            or "CylinderFeature" in feature_type
                        ):
                            details = get_primitive_details(entity)
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
