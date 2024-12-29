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


def format_timeline(timeline) -> str:
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
                if len(value) != 0:
                    md += f"{indent(tab_index)}{bold(format_python_variable(key))}:{DOUBLE_NEWLINE}"
                    md += read_list(value, tab_index + 1)
            else:
                md += f"{indent(tab_index)}{bold(format_python_variable(key))}: {value}"
            md += DOUBLE_NEWLINE
        return md

    md += read_dict(timeline, 0)

    return md


def write_to_file(file_path, json_data, write_in_md=True):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    json_data["json"] = compress_json(json_data)
    ordered_json_data = order_dict(json_data, Timeline)
    markdown = format_timeline(ordered_json_data)
    with open(file_path, "w", encoding="utf-8") as f:
        if write_in_md:
            f.write(markdown)
        else:
            json.dump(ordered_json_data, f, indent=2)
