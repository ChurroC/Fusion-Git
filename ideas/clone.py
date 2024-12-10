import adsk.core, adsk.fusion, traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get active design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get root component in this design
        rootComp = design.rootComponent

        bodyInSubComp1 = rootComp.bRepBodies.item(0)

        # Copy/paste body from sub component 1 to sub component 2
        copyPasteBody = rootComp.features.copyPasteBodies.add(bodyInSubComp1)

        rootComp.features.copyPasteBodies.add(sourceBodies)

        # Dump the information of Copy Paste Body in root component
        for copyPasteBody in rootComp.features.copyPasteBodies:
            copyPasteBodyInfo = "CopyPasteBody: name - {}".format(copyPasteBody.name)
            ui.messageBox(copyPasteBodyInfo)

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
