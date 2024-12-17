#Author-
#Description-
# import nah
import traceback
import adsk
from .nah import init
init()
from .nah import app, ui

ui.messageBox("s")

def funcc():
    try:
        app.activeDocument
        ui.m
        ui.messageBox('Hello script') 
        ui  = app.userInterface
        palettes = ui.palettes
        textPalette = palettes.itemById("TextCommands")
        textPalette.isVisible = True 
            
        textPalette.writeText("bh")
        adsk.doEvents() 

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
