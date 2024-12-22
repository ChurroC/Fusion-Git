from .globals import units_manager, error
import adsk.core

def format_value(value_input):
    """Format value using the design's default units"""
    try:
        return units_manager.formatValue(value_input)
    except:
        return str(value_input)


def get_point_data(point: adsk.core.Point3D):
    """Get coordinates from a point"""
    try:
        return {
            "x": format_value(point.x),
            "y": format_value(point.y),
            "z": format_value(getattr(point, "z", 0)),
        }
    except Exception as e:
        return error("Failed to get point data", e)

def remove_nulls(data):
    """Recursively removes null values from nested dictionaries and arrays."""
    if isinstance(data, dict):
        return {k: remove_nulls(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_nulls(item) for item in data if item is not None]
    else:
        return data