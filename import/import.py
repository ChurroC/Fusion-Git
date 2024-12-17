import adsk.core
import adsk.fusion
import traceback
import json


def run(context):
    try:
        global app, ui, design, units_manager, root, message
        message = ""
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        units_manager = adsk.fusion.FusionUnitsManager.cast(design.unitsManager)
        root = design.rootComponent

        fileDialog = ui.createFileDialog()
        fileDialog.title = "Select Timeline JSON File"
        fileDialog.filter = "JSON files (*.json)"

        if fileDialog.showOpen() != adsk.core.DialogResults.DialogOK:
            return

        import_timeline(fileDialog.filename)
        ui.messageBox(message)
    except:
        if ui:
            print_fusion(f"Failed:\n{traceback.format_exc()}")


def print_fusion(new_print: str):
    """Print to Fusion 360's console"""
    global message
    message += f"{new_print}\n"


def format_value(value_input):
    """Format value using the design's default units"""
    try:
        return units_manager.formatInternalValue(float(value_input))
    except:
        return str(value_input)


def get_point_data(point_str_data):
    """Extract coordinates from point string data"""
    try:
        return adsk.core.Point3D.create(
            units_manager.evaluateExpression(point_str_data["x"]),
            units_manager.evaluateExpression(point_str_data["y"]),
            units_manager.evaluateExpression(point_str_data["z"]),
        )
    except Exception as e:
        print_fusion(f"Error getting point data: {str(e)}")
        return None


def get_vector_data(vector_str_data):
    """Extract coordinates from vector string data"""
    try:
        return adsk.core.Vector3D.create(
            units_manager.evaluateExpression(vector_str_data["x"]),
            units_manager.evaluateExpression(vector_str_data["y"]),
            units_manager.evaluateExpression(vector_str_data["z"]),
        )
    except Exception as e:
        print_fusion(f"Error getting vector data: {str(e)}")
        return None

def create_plane(plane_data):
    """Try different methods to create a construction plane"""
    try:
        if (plane_data["type"] == "base_plane"): 
            # Kinda like enums maybe later when I seperate the files
            if (plane_data["name"] == "XY"):
                return root.xYConstructionPlane
            elif (plane_data["name"] == "XZ"):
                return root.xZConstructionPlane
            elif (plane_data["name"] == "YZ"):
                return root.yZConstructionPlane

        raise ValueError("All plane creation methods failed")
    except Exception as e:
        print_fusion(f"Error creating plane: {str(e)}")
        return None


def create_sketch_entities(sketch: adsk.fusion.Sketch, sketch_data):
    """Create sketch entities from sketch data"""
    try:
        for curve in sketch_data["curves"]:
            if curve["type"] == "adsk::fusion::SketchCircle":
                center = get_point_data(curve["centerPoint"])
                radius = units_manager.evaluateExpression(curve["radius"])
                if center and radius:
                    sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)

            elif curve["type"] == "adsk::fusion::SketchLine":
                start = get_point_data(curve["startPoint"])
                end = get_point_data(curve["endPoint"])
                if start and end:
                    sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    except Exception as e:
        print_fusion(f"Error creating sketch entities: {str(e)}")


def create_extrude(
    profile: adsk.fusion.Profile, extrude_data
):
    """Create an extrude feature"""
    try:
        # Create extrude input
        extrudes = root.features.extrudeFeatures
        
        # Set operation type based on exported data
        operation_map = {
            "0": adsk.fusion.FeatureOperations.JoinFeatureOperation,
            "1": adsk.fusion.FeatureOperations.CutFeatureOperation,
            "2": adsk.fusion.FeatureOperations.IntersectFeatureOperation,
            "3": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            "4": adsk.fusion.FeatureOperations.NewComponentFeatureOperation
        }
        
        operation = operation_map.get(
            extrude_data.get("operation", "3"),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        
        # Create the extrude input
        extrudeInput = extrudes.createInput(profile, operation)
        
        # Set the extent based on type
        extent_type = extrude_data["extent"]["type"]["value"]
        distance = extrude_data["extent"]["distance"]

        if extent_type == 0:  # OneSideFeatureExtentType            
            distance_extent = adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByString(distance["side_one"])
            )
            
            extrudeInput.setOneSideExtent(distance_extent, adsk.fusion.ExtentDirections.PositiveExtentDirection)
            
        elif extent_type == 1:  # TwoSidesFeatureExtentType
            extent_one = adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByString(distance["side_one"])
            )
            extent_two = adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByString(distance["side_two"])
            )
            
            extrudeInput.setTwoSidesExtent(extent_one, extent_two)
        elif extent_type == 2:  # SymmetricFeatureExtentType
            extrudeInput.setSymmetricExtent(adsk.core.ValueInput.createByString(distance["symmetric"]["value"]),
                                            bool(distance["symmetric"]["isFullLength"]))

        # Create the extrude
        extrude = extrudes.add(extrudeInput)
        print_fusion(f"Extrude created successfully with operation type: {operation}")
        return extrude
    except Exception as e:
        print_fusion(f"Error creating extrude: {str(e)}")
        return None


def import_timeline(file_path):
    """Import timeline from JSON file"""
    try:
        if not design:
            raise Exception("No active design")

        # Read JSON file
        with open(file_path, "r") as f:
            timeline_data = json.load(f)

        # Set document units
        if "units" in timeline_data:
            units_manager.distanceDisplayUnits = timeline_data["units"]["value"]

        # Process each feature
        for feature in timeline_data["features"]:
            print_fusion("")
            try:
                if feature["type"] == "adsk::fusion::Sketch":
                    print_fusion(f"Processing sketch: {feature['name']}")

                    plane = create_plane(feature["details"]["plane"])
                    print_fusion("Plane created")
      
                    # Create sketch
                    sketch = root.sketches.add(plane)
                    print_fusion("Sketch created")

                    # Add sketch entities
                    create_sketch_entities(sketch, feature["details"])

                elif feature["type"] == "adsk::fusion::ExtrudeFeature":
                    print_fusion(f"Processing extrude: {feature['name']}")

                    # Get the last sketch
                    if root.sketches.count == 0:
                        print_fusion("No sketch available for extrude")
                        continue

                    sketch = root.sketches.item(root.sketches.count - 1)

                    # Get the profile from the sketch
                    if sketch.profiles.count == 0:
                        print_fusion("No profile available in sketch")
                        continue

                    profile = sketch.profiles.item(0)

                    # Create extrude
                    extrude = create_extrude(profile, feature["details"])
                    if not extrude:
                        print_fusion("Failed to create extrude")
                        continue

            except Exception as e:
                print_fusion(f"Error processing feature {feature['index']}: {str(e)}")
                continue

        print_fusion("Timeline successfully imported")

    except Exception as e:
        print_fusion(f"Failed to import timeline: {str(e)}\n{traceback.format_exc()}")
