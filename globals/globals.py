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
        textPalette = adsk.core.TextCommandPalette.cast(palettes.itemById("TextCommands"))
        textPalette.isVisible = True
        textPalette.writeText(message)
        adsk.doEvents()
    except:
        error()

# This is my way to print to handle errors
def error(*args: str | Exception):
    reasons = ", ".join([reason for reason in args if not isinstance(reason, Exception)])
    exception_reasons = ", ".join([str(exception_reason) for exception_reason in args if isinstance(exception_reason, Exception)])
    print_fusion(f"Failed {reasons}: {exception_reasons}\n{traceback.format_exc()}")


# This is to intialize the global variables only on the first import
if "app" not in globals():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        units_manager = adsk.fusion.FusionUnitsManager.cast(design.unitsManager)
        print_fusion("") # Just to make sure the text palette is created
    except:
        error()