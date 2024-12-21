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
def error(*args: str | Exception | None):
    global ui
    
    info = None
    if args:
        for arg in args:
            if (arg):
                info = str(arg)
                break
    try:
        if ui:
            # got to us ui.messageBox since if it fails it never prints out message text
            print_fusion(f"""Failed {[f'to "{x}"' "," for x in args if not isinstance(x, Exception)]}: {[str(x) + "," for x in args if isinstance(x, Exception)]}\n{traceback.format_exc()}""")
    except: pass

# This is to intialize the global variables only on the first import
if "ui" not in globals():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        units_manager = adsk.fusion.FusionUnitsManager.cast(design.unitsManager)
        print_fusion("") # Just to make sure the text palette is created
    except:
        error()