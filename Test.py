# Author-Your Name
# Description-Export Valid Timeline Features

import adsk.core
import adsk.fusion
import traceback


def is_valid_feature(timeline_item):
    """
    Check if timeline item has an entity and is not a move feature
    """
    try:
        return (
            hasattr(timeline_item, "entity")
            and timeline_item.entity
            and timeline_item.entity.objectType != "adsk::fusion::MoveFeature"
        )
    except:
        return False


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get active design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get timeline
        timeline = design.timeline

        # Create a collection of valid timeline features
        features_collection = adsk.core.ObjectCollection.create()
        valid_features_info = []  # Store info about captured features

        # Add valid timeline items to collection
        for i in range(timeline.count):
            item = timeline.item(i)
            if is_valid_feature(item):
                features_collection.add(item.entity)
                valid_features_info.append(
                    {"index": i, "name": item.name, "type": item.entity.objectType}
                )

        if features_collection.count == 0:
            ui.messageBox("No valid features found in timeline.")
            return

        # Create copy feature input
        # copyFeatures = design.featuresdesign.features.copyFeatures
        # copyFeatureInput = copyFeatures.createInput(features_collection)

        rootComp = design.rootComponent
        copyFeatures = rootComp.features.copyPasteBodies
        # copyFeatures = adsk.fusion.CopyFileInput(features_collection)

        # Convert the feature input to Base64 string
        base64Str = copyFeatures.toBase64String()

        # Save to a text file
        try:
            fileDlg = ui.createFileDialog()
            fileDlg.isMultiSelectEnabled = False
            fileDlg.title = "Save Timeline Features"
            fileDlg.filter = "Text files (*.txt)"
            fileDlg.filterIndex = 0

            # Show file save dialog
            if fileDlg.showSave() == adsk.core.DialogResults.DialogOK:
                filepath = fileDlg.filename

                # Write to file
                with open(filepath, "w") as f:
                    f.write(base64Str)

                # Create summary message
                message = (
                    f"Successfully exported {features_collection.count} features:\n\n"
                )
                for info in valid_features_info:
                    message += f"{info['index'] + 1}. {info['name']}\n"
                    message += f"   Type: {info['type']}\n"
                message += f"\nSaved to:\n{filepath}"

                ui.messageBox(message)
        except:
            ui.messageBox("Failed to save file")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
