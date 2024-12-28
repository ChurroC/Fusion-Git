import os


def format_feature_details(details: dict) -> str:
    """Format the details of a feature into markdown strings."""
    if "error" in details:
        return f"&emsp;&emsp;&emsp;&emsp;error: {details['error']}\n"

    if isinstance(details, dict):
        markdown = ""
        # Handle component details
        if "is_linked" in details:
            markdown += f"&emsp;&emsp;&emsp;&emsp;details:\n\n"
            markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• is_linked: {str(details['is_linked']).lower()}\n\n"
            markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• is_component_creation: {str(details['is_component_creation']).lower()}\n\n"
            markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• id: {details['id']}"
        # Handle extrude details
        elif "operation" in details:
            operation_map = {0: "Cut", 1: "Join", 2: "Intersect", 3: "NewBody", 4: "CutIntersect"}
            markdown += f"&emsp;&emsp;&emsp;&emsp;details:\n\n"
            markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• operation: {operation_map[details['operation']]}\n\n"
            if "extent" in details and isinstance(details["extent"], dict):
                extent = details["extent"]
                if "error" not in extent:
                    markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• extent:\n\n"
                    if extent["type"] == 0:  # OneSideExtent
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;type: OneSide\n\n"
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;side_one: {extent['side_one']}"
                    elif extent["type"] == 1:  # TwoSidesExtent
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;type: TwoSides\n\n"
                        markdown += (
                            f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;side_one: {extent['side_one']}\n\n"
                        )
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;side_two: {extent['side_two']}"
                    elif extent["type"] == 2:  # SymmetricExtent
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;type: Symmetric\n\n"
                        markdown += (
                            f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;distance: {extent['distance']}\n\n"
                        )
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;isFullLength: {str(extent['isFullLength']).lower()}"
                else:
                    markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• extent: {extent['error']}\n"
        # Handle sketch details
        elif "curves" in details:
            markdown += f"&emsp;&emsp;&emsp;&emsp;details:\n\n"
            markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• curves:\n\n"
            for i, curve in enumerate(details["curves"], 1):
                if "error" in curve:
                    markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;{i}. error: {curve['error']}\n\n"
                else:
                    markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;{i}. type: {curve['type']}\n\n"
                    if curve["type"] == "adsk::fusion::SketchCircle":
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;center: ({curve['center_point']['x']}, {curve['center_point']['y']}, {curve['center_point']['z']})\n\n"
                        markdown += (
                            f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;radius: {curve['radius']}\n\n"
                        )
                    elif curve["type"] == "adsk::fusion::SketchLine":
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;start: ({curve['start_point']['x']}, {curve['start_point']['y']}, {curve['start_point']['z']})\n\n"
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;end: ({curve['end_point']['x']}, {curve['end_point']['y']}, {curve['end_point']['z']})\n\n"

            if "plane" in details:
                plane = details["plane"]
                if "error" in plane:
                    markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• plane: {plane['error']}\n"
                else:
                    markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;• plane:\n\n"
                    markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;type: {plane['type']}\n\n"
                    if plane["type"] == "custom_plane":
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;index: {plane['index']}\n"
                    elif plane["type"] == "base_plane":
                        markdown += f"&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;name: {plane['name']}\n"

        return markdown

    return ""


def timeline_to_markdown(timeline: dict) -> str:
    """
    Convert timeline data to markdown format.

    Args:
        timeline: Timeline data structure

    Returns:
        str: Formatted markdown string
    """
    markdown = "**document_name**\n\n"
    markdown += f"&emsp;&emsp;- {timeline['document_name']}\n\n"

    markdown += "**units**\n\n"
    markdown += f"&emsp;&emsp;- {timeline['units']}\n\n"

    if "info" in timeline:
        markdown += "**info**\n\n"
        info = timeline["info"]
        markdown += f"&emsp;&emsp;• link: {str(info['link'])}\n\n"
        markdown += f"&emsp;&emsp;• component_reference: {str(info['component_reference']).lower()}\n\n"
        markdown += f"&emsp;&emsp;• component_reference_id: {info['component_reference_id']}\n\n"
        markdown += f"&emsp;&emsp;• component_creation_name: {info['component_creation_name']}\n\n"

    markdown += "**features**\n\n"

    if len(timeline["features"]) != 0:
        for i, feature in enumerate(timeline["features"], 1):
            if "error" in feature:
                markdown += f"&emsp;&emsp;{i}. error: {feature['error']}\n\n"
                continue

            markdown += f"&emsp;&emsp;{i}. **{feature['name']}**\n\n"
            markdown += f"&emsp;&emsp;&emsp;&emsp;type: {feature['type']}\n\n"
            markdown += format_feature_details(feature["details"]) + "\n\n"

    return markdown.rstrip()


def write_to_file(file_path, json_data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    markdown = timeline_to_markdown(json_data)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)
