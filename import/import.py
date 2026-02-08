# Author-
# Description-
# import nah
import adsk.core, adsk.fusion
from typing import cast
import json

from .globals.globals import ui, units_manager, active_document, error, print_fusion
from .globals.types import Data, Feature, Error

from .features.features import FEATURE_HANDLER


def run(context):
    try:
        fileDialog = ui.createFileDialog()
        fileDialog.title = "Select Timeline JSON File"
        fileDialog.filter = "JSON files (*.json)"

        if fileDialog.showOpen() != adsk.core.DialogResults.DialogOK:
            return

        with open(fileDialog.filename, "r") as f:
            timeline_data: Data = json.load(f)

        active_document.name = timeline_data["components"]["root"]["name"]
        # units_manager.distanceDisplayUnits = timeline_data["components"]["root"]["units"]

        stats = process_timeline(timeline_data["timeline"])

        print_fusion(
            f"Timeline import completed: "
            f"{stats['success']} succeeded, "
            f"{stats['failed']} failed, "
            f"{stats['skipped']} skipped"
        )
    except Exception as e:
        error("Failed to import timeline", e)


def process_timeline(timeline: list[Feature | Error]) -> dict[str, int]:
    stats = {"success": 0, "failed": 0, "skipped": 0}
    total = len(timeline)

    for index, feature in enumerate(timeline, 1):
        feature_name = feature.get("name", "unknown")
        print_fusion(f"[{index}/{total}] Processing: {feature_name}")

        result = set_feature_data(feature)
        stats[result] += 1

    return stats


def set_feature_data(feature: Feature | Error) -> str:
    try:
        if "error" in feature:
            print_fusion(f"Skipped feature with error: {feature.get('error')}")
            return "skipped"

        feature_type = feature["type"]["value"]  # Get the actual type string from ReadableValue
        feature_name = feature["name"]

        if feature_type not in FEATURE_HANDLER:
            print_fusion(f"  ⊗ Unsupported feature type: {feature_type}")
            return "skipped"

        # Execute the handler
        handler = FEATURE_HANDLER[feature_type]
        handler(feature["details"])

        print_fusion(f"Made: {feature_name}")
        return "success"
    except Exception as e:
        error("Failed to process feature", e)
        return "failed"
