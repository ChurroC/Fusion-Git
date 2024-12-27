import adsk.core, adsk.fusion, adsk.cam, traceback
from .types.types import Error

# These are the defaults for the Fusion 360 API
app: adsk.core.Application
ui: adsk.core.UserInterface
design: adsk.fusion.Design
units_manager: adsk.fusion.FusionUnitsManager
root: adsk.fusion.Component
active_document: adsk.core.Document


# This is my way to print to the Fusion 360 UI
def print_fusion(*args: str):
    global ui
    try:
        palettes = ui.palettes
        textPalette = adsk.core.TextCommandPalette.cast(palettes.itemById("TextCommands"))
        textPalette.isVisible = True
        textPalette.writeText(" ".join([str(arg) for arg in args]))
        adsk.doEvents()
    except Exception as e:
        error("Failed to print error", e)


# This is my way to print to handle errors
def error(*args: str | Exception):
    reasons = ", ".join([reason for reason in args if not isinstance(reason, Exception)])
    exception_reasons = ", ".join(
        [str(exception_reason) for exception_reason in args if isinstance(exception_reason, Exception)]
    )
    print_fusion(f"{reasons}: {exception_reasons}\n{traceback.format_exc()}")

    error_data: Error = {"error": f"{reasons}: {exception_reasons}"}
    return error_data


# This is to intialize the global variables only on the first import
if "ui" not in globals():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        print_fusion("")  # Just to make sure the text palette is created
        print_fusion("")  # Just to make sure the text palette is created
        print_fusion("")  # Just to make sure the text palette is created
        print_fusion("")  # Just to make sure the text palette is created
        print_fusion("")  # Just to make sure the text palette is created
        print_fusion("")  # Just to make sure the text palette is created
        print_fusion("")  # Just to make sure the text palette is created
        print_fusion("")  # Just to make sure the text palette is created
        print_fusion("")  # Just to make sure the text palette is created
        design = adsk.fusion.Design.cast(app.activeProduct)
        units_manager = adsk.fusion.FusionUnitsManager.cast(design.unitsManager)
        root = design.rootComponent
        active_document = app.activeDocument
    except Exception as e:
        if ui:
            error("Failed to initialize globals", e)
            # if there is no ui then manually open text palette and read the script error
            # Option + CMD + C on Mac OS or ALT + CTRL + C on Windows OS
