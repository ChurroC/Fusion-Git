# Author-Your Name
# Description-Get All Extrusions in Design

import adsk.core
import adsk.fusion
import traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get active design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Create collection to store all extrusions
        all_extrusions = []

        # Function to process components recursively
        def process_component(component):
            # Get features from current component
            features = component.features

            # Get all extrude features
            extrudes = features.extrudeFeatures
            for extrude in extrudes:
                all_extrusions.append(
                    {
                        "component": component.name,
                        "feature": extrude,
                        "name": extrude.name,
                    }
                )

            # Process all occurrences (sub-components)
            for occurrence in component.occurrences:
                process_component(occurrence.component)

        # Start processing from root component
        process_component(design.rootComponent)

        # Create detailed message about found extrusions
        message = f"Found {len(all_extrusions)} extrusion(s):\n\n"

        for i, ext in enumerate(all_extrusions, 1):
            extrude = ext["feature"]
            message += f"{i}. Extrusion: {ext['name']}\n"
            message += f"   Component: {ext['component']}\n"

            # Get operation type
            op_types = {
                adsk.fusion.FeatureOperations.JoinFeatureOperation: "Join",
                adsk.fusion.FeatureOperations.CutFeatureOperation: "Cut",
                adsk.fusion.FeatureOperations.IntersectFeatureOperation: "Intersect",
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation: "New Body",
            }
            op_type = op_types.get(extrude.operation, "Unknown")
            message += f"   Operation: {op_type}\n"

            # Get extent details
            extent = extrude.extentOne
            if extent.distance:
                message += f"   Distance: {extent.distance} cm\n"

            # # Get direction info
            # if extrude.isSymmetric:
            #     message += "   Direction: Symmetric\n"
            # else:
            #     message += "   Direction: Single direction\n"

            # Check for surface vs solid
            message += "   Type: "
            message += "Solid" if extrude.isSolid else "Surface"
            message += "\n\n"

        ui.messageBox(message)

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
