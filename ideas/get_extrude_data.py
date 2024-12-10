# Fusion360API Python script

import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app: adsk.core.Application = adsk.core.Application.get()
        ui: adsk.core.UserInterface = app.userInterface
        design: adsk.fusion.Design = app.activeProduct
        rootComponent: adsk.fusion.Component = design.rootComponent
        product = app.activeProduct

        features = rootComponent.features 

        extrudes = adsk.fusion.ExtrudeFeatures.cast(design.rootComponent.features.extrudeFeatures)
        extrude = extrudes[0]

        text = ""
        for each_extrude in extrudes:
            text += each_extrude.name + "\n"
        ui.messageBox(text)

        ui.messageBox(extrude.name)
        extentOne = extrude.extentOne 


        distanceDef = adsk.fusion.DistanceExtentDefinition.cast(extentOne) 

        ui.messageBox(str(distanceDef.distance.value))
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
