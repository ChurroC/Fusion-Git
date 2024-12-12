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


def get_sketch_data(sketch):
    """Get details about a sketch feature"""
    try:
        data = {}
        data["profiles_count"] = sketch.profiles.count
        data["curves_count"] = sketch.sketchCurves.count

        # Count curve types
        lines_count = 0
        circles_count = 0
        arcs_count = 0

        for curve in sketch.sketchCurves:
            if isinstance(curve, adsk.fusion.SketchLine):
                lines_count += 1
            elif isinstance(curve, adsk.fusion.SketchCircle):
                circles_count += 1
            elif isinstance(curve, adsk.fusion.SketchArc):
                arcs_count += 1

        if lines_count > 0:
            data["SketchLines"] = lines_count
        if circles_count > 0:
            data["SketchCircles"] = circles_count
        if arcs_count > 0:
            data["SketchArcs"] = arcs_count

        return data
    except:
        return {"error": "Failed to get sketch details"}


def get_extrude_data(extrude):
    """Get details about an extrude feature"""
    try:
        data = {}

        # Get faces created by extrude
        if hasattr(extrude, "faces"):
            faces = extrude.faces
            data["faces_count"] = faces.count

        # Try to get extrude properties
        if hasattr(extrude, "extentOne"):
            extent = extrude.extentOne
            if extent and hasattr(extent, "distance"):
                data["distance"] = format_value(extent.distance.value)

        # Get operation type
        if hasattr(extrude, "operation"):
            operation_types = {
                adsk.fusion.FeatureOperations.CutFeatureOperation: "Cut",
                adsk.fusion.FeatureOperations.JoinFeatureOperation: "Join",
                adsk.fusion.FeatureOperations.IntersectFeatureOperation: "Intersect",
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation: "New Body",
            }
            data["operation"] = operation_types.get(extrude.operation, "Unknown")

        return data
    except:
        return {"error": "Failed to get extrude details"}


def export_timeline(save_path):
    """Export timeline to JSON file"""
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
                    feature_data["details"] = get_sketch_data(entity)
                elif "ExtrudeFeature" in feature_type:
                    feature_data["details"] = get_extrude_data(entity)

                export_data["features"].append(feature_data)

            except:
                print(f"Error processing feature {i + 1}")
                continue

        # Write to JSON file
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        return True, "Timeline successfully exported"

    except:
        return False, f"Failed to export timeline:\n{traceback.format_exc()}"


def stop(context):
    pass
