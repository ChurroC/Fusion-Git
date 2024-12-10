import adsk.core, adsk.fusion, traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get root component
        rootComp = design.rootComponent

        # Create new sketch on XY plane
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)

        # Get sketch lines
        lines = sketch.sketchCurves.sketchLines

        # Create rectangle by two points
        startPoint = adsk.core.Point3D.create(0, 0, 0)
        endPoint = adsk.core.Point3D.create(5, 3, 0)  # 5cm x 3cm rectangle
        lines.addTwoPointRectangle(startPoint, endPoint)

        # Get the profile of the sketch
        profile = sketch.profiles.item(0)

        # Create extrusion
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(
            profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )

        # Define the extrusion distance
        distance = adsk.core.ValueInput.createByReal(2.0)  # 2cm high
        extInput.setDistanceExtent(False, distance)

        # Create the extrusion
        extrudes.add(extInput)

        ui.messageBox("Box created successfully!")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
