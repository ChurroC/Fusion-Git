# Author - ChurroC
# Description - Export timeline data to a JSON file

from typing import Literal, cast
import adsk.core, adsk.fusion
import os

from .globals.globals import ui, units_manager, design, error, print_fusion, app
from .globals.types import (
    Timeline,
    Feature,
    SketchFeature,
    ExtrudeFeature,
    Error,
    ComponentFeature,
    FusionComponentTimeline,
)
from .display_data import write_to_file
from .features import get_sketch_data, get_extrude_data
from .globals.utils import create_readable_value

component_timeline: FusionComponentTimeline


import adsk.core, adsk.fusion


def run(context):
    try:
        root_comp = design.rootComponent

        # Get the first occurrence
        if root_comp.occurrences.count > 0:
            first_occurrence = root_comp.occurrences.item(0)
            # Get the component from the occurrence
            component = first_occurrence.component

            # Now get features from the component
            all_features = component.features

            for feature in all_features:
                print_fusion(f"Feature: {feature.name}")

        else:
            ui.messageBox("No occurrences found in the active design.")

    except Exception as e:
        error("Failed to export timeline", e)
