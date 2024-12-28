import os
from typing import Mapping

from .globals.types.types import Timeline

BASE_INDENT = "&emsp;&emsp;"  # Two &emsp; for each level
BULLET = "•"
NEWLINE = "\n"
DOUBLE_NEWLINE = "\n\n"

OPERATION_MAP = {0: "Cut", 1: "Join", 2: "Intersect", 3: "NewBody", 4: "CutIntersect"}


def get_indent(level: int) -> str:
    """Get indentation for given level."""
    return BASE_INDENT * level


def format_bullet_item(level: int, key: str, value: str) -> str:
    """Format a bullet point item."""
    return f"{get_indent(level)}{BULLET} {key}: {value}{DOUBLE_NEWLINE}"


def format_type_line(level: int, type_str: str) -> str:
    """Format a type line."""
    return f"{get_indent(level)}type: {type_str}{DOUBLE_NEWLINE}"


def format_header(text: str) -> str:
    """Format a header."""
    return f"**{text}**{DOUBLE_NEWLINE}"


def format_numbered_item(level: int, number: int, text: str) -> str:
    """Format a numbered item."""
    return f"{get_indent(level)}{number}. {format_header(text)}"


def format_point3d(point: dict) -> str:
    """Format a 3D point."""
    return f"({point['x']}, {point['y']}, {point['z']})"


def format_component_details(details: dict, level: int) -> str:
    """Format component details."""
    md = f"{get_indent(level)}details:{DOUBLE_NEWLINE}"
    md += format_bullet_item(level + 1, "is_linked", str(details["is_linked"]).lower())
    md += format_bullet_item(level + 1, "is_component_creation", str(details["is_component_creation"]).lower())
    md += format_bullet_item(level + 1, "id", details["id"])
    return md


def format_extrude_details(details: dict, level: int) -> str:
    """Format extrude details."""
    md = f"{get_indent(level)}details:{DOUBLE_NEWLINE}"
    md += format_bullet_item(level + 1, "operation", OPERATION_MAP[details["operation"]])

    if "extent" in details and isinstance(details["extent"], dict):
        extent = details["extent"]
        if "error" not in extent:
            md += f"{get_indent(level + 1)}{BULLET} extent:{DOUBLE_NEWLINE}"
            extent_level = level + 2

            extent_types = {
                0: ("OneSide", ["side_one"]),
                1: ("TwoSides", ["side_one", "side_two"]),
                2: ("Symmetric", ["distance", "isFullLength"]),
            }

            if extent["type"] in extent_types:
                type_name, fields = extent_types[extent["type"]]
                md += f"{get_indent(extent_level)}type: {type_name}{DOUBLE_NEWLINE}"
                for field in fields:
                    value = str(extent[field]).lower() if field == "isFullLength" else extent[field]
                    md += f"{get_indent(extent_level)}{field}: {value}{DOUBLE_NEWLINE}"
        else:
            md += format_bullet_item(level + 1, "extent", extent["error"])

    return md


def format_sketch_details(details: dict, level: int) -> str:
    """Format sketch details."""
    md = f"{get_indent(level)}details:{DOUBLE_NEWLINE}"
    md += f"{get_indent(level + 1)}{BULLET} curves:{DOUBLE_NEWLINE}"

    for i, curve in enumerate(details["curves"], 1):
        if "error" in curve:
            md += f"{get_indent(level + 2)}{i}. error: {curve['error']}{DOUBLE_NEWLINE}"
            continue

        md += f"{get_indent(level + 2)}{i}. type: {curve['type']}{DOUBLE_NEWLINE}"

        if curve["type"] == "adsk::fusion::SketchCircle":
            md += f"{get_indent(level + 3)}center: {format_point3d(curve['center_point'])}{DOUBLE_NEWLINE}"
            md += f"{get_indent(level + 3)}radius: {curve['radius']}{DOUBLE_NEWLINE}"
        elif curve["type"] == "adsk::fusion::SketchLine":
            md += f"{get_indent(level + 3)}start: {format_point3d(curve['start_point'])}{DOUBLE_NEWLINE}"
            md += f"{get_indent(level + 3)}end: {format_point3d(curve['end_point'])}{DOUBLE_NEWLINE}"

    if "plane" in details:
        plane = details["plane"]
        if "error" in plane:
            md += format_bullet_item(level + 1, "plane", plane["error"])
        else:
            md += f"{get_indent(level + 1)}{BULLET} plane:{DOUBLE_NEWLINE}"
            md += f"{get_indent(level + 2)}type: {plane['type']}{DOUBLE_NEWLINE}"
            if plane["type"] == "custom_plane":
                md += f"{get_indent(level + 2)}index: {plane['index']}{DOUBLE_NEWLINE}"
            elif plane["type"] == "base_plane":
                md += f"{get_indent(level + 2)}name: {plane['name']}{DOUBLE_NEWLINE}"

    return md


def format_feature_details(details: dict) -> str:
    """Format feature details based on their type."""
    if "error" in details:
        return f"{get_indent(2)}error: {details['error']}{NEWLINE}"

    if not isinstance(details, dict):
        return ""

    # Determine the type of details and use appropriate formatter
    if "is_linked" in details:
        return format_component_details(details, 2)
    elif "operation" in details:
        return format_extrude_details(details, 2)
    elif "curves" in details:
        return format_sketch_details(details, 2)

    return ""


def format_timeline(timeline: dict) -> str:
    """Format the entire timeline."""
    md = ""

    # Document name
    md += format_header("document_name")
    md += f"{get_indent(1)}- {timeline['document_name']}{DOUBLE_NEWLINE}"

    # Units
    md += format_header("units")
    md += f"{get_indent(1)}- {timeline['units']}{DOUBLE_NEWLINE}"

    # Features
    md += format_header("features")

    for i, feature in enumerate(timeline["features"], 1):
        if "error" in feature:
            md += format_numbered_item(1, i, f"error: {feature['error']}")
            continue

        md += format_numbered_item(1, i, feature["name"])
        md += format_type_line(2, feature["type"])
        md += format_feature_details(feature["details"])

    return md


BASE_INDENT = "&emsp;&emsp;"  # Two &emsp; for each level
DOUBLE_NEWLINE = "\n\n"


def format_python_variable(word: str) -> str:
    return word.replace("_", " ").title()


def bold(word: str) -> str:
    return f"**{word}**"


def indent(level: int) -> str:
    """Get indentation for given level."""
    return BASE_INDENT * level


def format_timeline2(timeline) -> str:
    """Format the entire timeline."""
    md = ""

    def read_list(lst: list, tab_index: int) -> str:
        md = ""
        for index, value in enumerate(lst, 1):
            if isinstance(value, dict):
                if "error" in value:
                    md += f"{value['error']}"
                elif "md" in value:
                    md += f"{value['md']}"
                else:
                    md += f"{indent(tab_index)}{index}:{DOUBLE_NEWLINE}"
                    md += read_dict(value, tab_index + 1)
            elif isinstance(value, list):
                md += read_list(value, tab_index + 1)
            else:
                md += f"{value}"
            md += DOUBLE_NEWLINE
        return md

    def read_dict(dictionary, tab_index: int) -> str:
        md = ""
        for key, value in dictionary.items():
            if isinstance(value, dict):
                if "error" in value:
                    md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value['error']}"
                elif "md" in value:
                    md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value['md']}"
                else:
                    md += f"{indent(tab_index)}{bold(format_python_variable(key))}:{DOUBLE_NEWLINE}"
                    md += read_dict(value, tab_index + 1)
            elif isinstance(value, list):
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}:{DOUBLE_NEWLINE}"
                md += read_list(value, tab_index + 1)
            else:
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value}"
            md += DOUBLE_NEWLINE
        return md

    md += read_dict(timeline, 0)

    print("FINAL")
    print("FINAL")
    print("FINAL")
    print("FINAL")
    print("FINAL")
    print("FINAL")
    return md


def write_markdown_to_file(file_path, json_data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    markdown = format_timeline2(json_data)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)
