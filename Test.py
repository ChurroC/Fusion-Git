import adsk.core, adsk.fusion, traceback


def create_extrude(sketch_name, distance, operation_type):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = app.activeProduct
    rootComp = design.rootComponent

    # Get the sketch
    sketch = rootComp.sketches.itemByName(sketch_name)
    if not sketch:
        raise Exception(f'Sketch "{sketch_name}" not found')

    # Get the profile
    profiles = sketch.profiles
    if profiles.count == 0:
        raise Exception("No profile found in the sketch")

    # Create extrusion input
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(profiles.item(0), operation_type)

    # Set the extrusion distance
    dist_value = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(f"{distance} in")
    )
    extInput.setOneSideExtent(
        dist_value, adsk.fusion.ExtentDirections.PositiveExtentDirection
    )

    # Create the extrusion
    return extrudes.add(extInput)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Example usage
        extrude = create_extrude(
            sketch_name="Sketch8",
            distance=10.0,
            operation_type=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        )

        ui.messageBox("Extrusion completed successfully")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
