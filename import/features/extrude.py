import adsk.fusion, adsk.core
from ..globals.types import Error, ExtrudeExtent, ExtrudeDetails
from ..globals.globals import error, root


def set_extrude_data(extrude_details: ExtrudeDetails | Error) -> None:
    try:
        if "error" in extrude_details:
            raise Exception("Failed to read extrude error data")

        if root.sketches.count == 0:
            raise Exception("No sketch available for extrude")

        sketch = root.sketches.item(root.sketches.count - 1)

        if sketch.profiles.count == 0:
            raise Exception("No profile available in sketch")

        profile = sketch.profiles.item(0)

        # Create the extrude input
        extrudes = root.features.extrudeFeatures
        operation = extrude_details["operation"]["value"]
        extrude_input = extrudes.createInput(profile, operation)

        set_extent_data(extrude_input, extrude_details["extent"])

        extrudes.add(extrude_input)

    except Exception as e:
        error("Failed to process extrude", e)


def set_extent_data(extrude_input: adsk.fusion.ExtrudeFeatureInput, extent_data: ExtrudeExtent | Error) -> None:
    if "error" in extent_data:
        raise Exception("Failed to read extrude extent error data")

    extent_type = extent_data["type"]["value"]

    if extent_type == 0:  # OneSideFeatureExtentType
        distance_extent = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByString(extent_data["side_one"])
        )
        extrude_input.setOneSideExtent(distance_extent, adsk.fusion.ExtentDirections.PositiveExtentDirection)

    elif extent_type == 1:  # TwoSidesFeatureExtentType
        extent_one = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByString(extent_data["side_one"])
        )
        extent_two = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByString(extent_data["side_two"])
        )
        extrude_input.setTwoSidesExtent(extent_one, extent_two)

    elif extent_type == 2:  # SymmetricFeatureExtentType
        distance = adsk.core.ValueInput.createByString(extent_data["distance"])
        is_full_length = bool(extent_data["isFullLength"])
        extrude_input.setSymmetricExtent(distance, is_full_length)

    else:
        raise Exception(f"Unknown extent type: {extent_type}")
