from typing import Mapping
import json
import platform
import os

from .globals.globals import print_fusion
from .order_json import order_dict
from .globals.types import Data, ComponentInfo
from .globals.utils import compress_json

BASE_INDENT = "&emsp;&emsp;"  # Two &emsp; for each level
DOUBLE_NEWLINE = "\n\n"


def format_python_variable(word: str) -> str:
    return word.replace("_", " ").title()


def bold(word: str) -> str:
    return f"**{word}**"


def indent(level: int) -> str:
    """Get indentation for given level."""
    return BASE_INDENT * level


def read_list_md(lst: list, tab_index: int = 0) -> str:
    md = ""
    for index, value in enumerate(lst, 1):
        if isinstance(value, dict):
            md += f"{indent(tab_index)}{index}:{DOUBLE_NEWLINE}"
            md += read_dict_md(value, tab_index + 1)
        elif isinstance(value, list):
            md += read_list_md(value, tab_index + 1)
        else:
            md += f"{indent(tab_index)}{index}: {value}{DOUBLE_NEWLINE}"
    return md


def read_dict_md(dictionary: Mapping, tab_index: int = 0) -> str:
    md = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            if "error" in value:
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value['error']}{DOUBLE_NEWLINE}"
            elif "md" in value:
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value['md']}{DOUBLE_NEWLINE}"
            elif "display" in value:
                pass
            else:
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}:{DOUBLE_NEWLINE}"
                md += read_dict_md(value, tab_index + 1)
        elif isinstance(value, list):
            if len(value) != 0:
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}:{DOUBLE_NEWLINE}"
                md += read_list_md(value, tab_index + 1)
        else:
            md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value}{DOUBLE_NEWLINE}"
    return md


def write_to_file(file_path, json_data: list | Mapping, write_in_md=True):
    path = file_path.rsplit(".", 1)[0] + (".json" if not write_in_md else ".md")
    path = os.path.abspath(path)

    # Only add Windows UNC prefix on Windows for long paths
    if platform.system() == "Windows" and len(path) > 260:
        path = r"\\?\\" + path

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if write_in_md:
            if isinstance(json_data, list):
                markdown = read_list_md(json_data)
            else:
                markdown = read_dict_md(json_data)
            f.write(markdown)
        else:
            json.dump(json_data, f, indent=2)


# Still got to do references
# If Cube is refernece in linked_component for another component liked lined component but should I ned up having 2 folder for it
# ALso all names in data josn same
def write_nested_data(src_file_path, json_data: Data, write_in_md=True, write_data_file=True):
    ordered_json = order_dict(json_data, Data)
    components = ordered_json["components"]

    if write_data_file:
        write_to_file(os.path.join(src_file_path, components["root"]["path"], "data.json"), ordered_json, False)

    for component in components.values():
        if component["is_linked"] and "assembly" in component:
            assembly_data = component["assembly"]["value"]
            assembly_data["components"]["root"] = {
                **assembly_data["components"]["root"],
                "index": component["index"] if "index" in component else 0,
                "references": component["references"],
            }
            write_nested_data(
                src_file_path,
                assembly_data,
                write_in_md,
                False,
            )
        else:
            write_to_file(
                os.path.join(src_file_path, component["path"], "timeline.json"),
                component,
                write_in_md,
            )
            if component["references"]:
                for reference in component["references"]:
                    write_to_file(
                        os.path.join(src_file_path, reference["path"], "timeline.json"),
                        reference,
                        write_in_md,
                    )
