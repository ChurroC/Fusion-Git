import json
import os
from .order_json import order_dict
from .globals.types import Timeline
from .globals.compression import compress_json

BASE_INDENT = "&emsp;&emsp;"  # Two &emsp; for each level
DOUBLE_NEWLINE = "\n\n"


def format_python_variable(word: str) -> str:
    return word.replace("_", " ").title()


def bold(word: str) -> str:
    return f"**{word}**"


def indent(level: int) -> str:
    """Get indentation for given level."""
    return BASE_INDENT * level


def read_list_md(lst: list, tab_index: int) -> str:
    md = ""
    for index, value in enumerate(lst, 1):
        if isinstance(value, dict):
            if "error" in value:
                md += f"{indent(tab_index)}{value['error']}{DOUBLE_NEWLINE}"
            elif "md" in value:
                md += f"{indent(tab_index)}{value['md']}:{DOUBLE_NEWLINE}"
            else:
                md += f"{indent(tab_index)}{index}:{DOUBLE_NEWLINE}"
                md += read_dict_md(value, tab_index + 1)
        elif isinstance(value, list):
            md += read_list_md(value, tab_index + 1)
        else:
            md += f"{indent(tab_index)}{value['md']}:{DOUBLE_NEWLINE}"
    return md


def read_dict_md(dictionary, tab_index: int = 0) -> str:
    md = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            if "error" in value:
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value['error']}{DOUBLE_NEWLINE}"
            elif "md" in value:
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value['md']}{DOUBLE_NEWLINE}"
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


def write_to_file(file_path, json_data, write_in_md=True):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    json_data["json"] = compress_json(json_data)
    ordered_json_data = order_dict(json_data, Timeline)
    with open(file_path, "w", encoding="utf-8") as f:
        if write_in_md:
            markdown = read_dict_md(ordered_json_data)
            f.write(markdown)
        else:
            json.dump(ordered_json_data, f, indent=2)
