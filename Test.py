# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the active design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component timeline
        timeline = design.timeline

        # Get the number of timeline items
        numTimelineItems = timeline.count

        # Create a message to store timeline info
        message = f"Number of timeline items: {numTimelineItems}\n\n"

        # Iterate through timeline items
        for i in range(numTimelineItems):
            item = timeline.item(i)  # Get specific timeline item
            message += f"Item {i + 1}: {item.name} (Type: {item.objectType})\n"

            # Check if item is suppressed
            if item.isSuppressed:
                message += "   - Status: Suppressed\n"
            else:
                message += "   - Status: Active\n"

        # Display the timeline information
        ui.messageBox(message)

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
