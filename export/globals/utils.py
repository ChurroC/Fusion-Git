import adsk.core

from typing import TypeVar
import json
import base64
import zlib

from .globals import units_manager
from .types import Point3D, ReadableValue


def format_value(value_input, include_units: bool = False):
    """Format value with optional units
    Args:
        value_input: The value to format
        include_units: Whether to include units in the output (default: False)
    """
    try:
        formatted = units_manager.formatValue(value_input)
        return formatted if include_units else formatted.split(" ")[0]
    except:
        return str(value_input)


def get_point_data(point: adsk.core.Point3D) -> Point3D:
    x = format_value(point.x)
    y = format_value(point.y)
    z = format_value(point.z)
    return {
        "md": f"({x}, {y}, {z})",
        "value": {
            "x": x,
            "y": y,
            "z": z,
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


def compress_json(data):
    """Compress JSON data using zlib with maximum compression."""
    json_str = json.dumps(data, separators=(",", ":"))
    compressed = zlib.compress(json_str.encode(), level=9)
    return base64.b64encode(compressed).decode()


def decompress_json(compressed_str):
    """Decompress a zlib-compressed JSON string back to data."""
    decoded = base64.b64decode(compressed_str)
    json_str = zlib.decompress(decoded).decode()
    return json.loads(json_str)
