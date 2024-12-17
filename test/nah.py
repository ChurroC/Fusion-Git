import adsk.core, adsk.fusion, adsk.cam, traceback


app: adsk.core.Application
ui: adsk.core.UserInterface
design, units_manager, message

def init():
    try:
        global app, ui, design, units_manager, message
        message = ""
        app: adsk.core.Application = adsk.core.Application.get()
        ui: adsk.core.UserInterface = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        units_manager = adsk.fusion.FusionUnitsManager.cast(design.unitsManager)
    except:
        if ui:
            # got to us ui.messageBox since if it fails it never prints out message text
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")
            
def print_fusion():
    "S"