import adsk.core, adsk.fusion, adsk.cam, traceback

# These are the defaults for the Fusion 360 API
app: adsk.core.Application
ui: adsk.core.UserInterface
design: adsk.fusion.Design
units_manager: adsk.fusion.FusionUnitsManager

# This is my way to print to the Fusion 360 UI
def print_fusion(message: str):
    global ui
    try:
        palettes = ui.palettes
        textPalette = palettes.itemById("TextCommands")
        textPalette.isVisible = True
        textPalette.writeText(message)
        adsk.doEvents()
    except:
        error()

# This is my way to print to handle erro 
def error():
    global ui
    try:
        if ui:
            # got to us ui.messageBox since if it fails it never prints out message text
            print_fusion(f"Failed:\n{traceback.format_exc()}")
    except: pass

# This is to intialize the global variables only on the first import
if "ui" not in globals():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        units_manager = adsk.fusion.FusionUnitsManager.cast(design.unitsManager)
    except:
        error()