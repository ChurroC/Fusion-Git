import json
import os
from typing import TypeVar
from .globals import units_manager
from .types import Point3D, ReadableValue
import adsk.core


def format_value(value_input):
    """Format value using the design's default units"""
    try:
        return units_manager.formatValue(value_input)
    except:
        return str(value_input)


def get_point_data(point: adsk.core.Point3D) -> Point3D:
    return {
        "md": f"({point.x}, {point.y}, {getattr(point, "z", 0)})",
        "value": {
            "x": format_value(point.x),
            "y": format_value(point.y),
            "z": format_value(getattr(point, "z", 0)),
        },
    }


def set_point_data(point: Point3D):
    return adsk.core.Point3D.create(
        units_manager.evaluateExpression(point["value"]["x"]),
        units_manager.evaluateExpression(point["value"]["y"]),
        units_manager.evaluateExpression(point["value"]["z"]),
    )


def remove_nulls(data):
    """Recursively removes null values from nested dictionaries and arrays."""
    if isinstance(data, dict):
        return {k: remove_nulls(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_nulls(item) for item in data if item is not None]
    else:
        return data


def write_to_file(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# This is a pretty fast way to search for a key through a nested dictionary
# Instead of reading path by path for finding a component source path I could use this
# I could also use this to find the occurrence of a component in the timeline which is useful for joints
def gen_dict_extract(key, var):
    if hasattr(var, "items"):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


Value = TypeVar("Value")


def create_readable_value(md: str, value: Value) -> ReadableValue[Value]:
    return {"md": md, "value": value}
