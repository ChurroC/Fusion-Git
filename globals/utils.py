import json
import os
from .globals import units_manager
from .types.types import Point3D
import adsk.core

def format_value(value_input):
    """Format value using the design's default units"""
    try:
        return units_manager.formatValue(value_input)
    except:
        return str(value_input)


def get_point_data(point: adsk.core.Point3D) -> Point3D:
    return {
        "x": format_value(point.x),
        "y": format_value(point.y),
        "z": format_value(getattr(point, "z", 0)),
    }

def set_point_data(point: Point3D):
    return adsk.core.Point3D.create(
            units_manager.evaluateExpression(point["x"]),
            units_manager.evaluateExpression(point["y"]),
            units_manager.evaluateExpression(point["z"]),
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
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)