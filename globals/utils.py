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
        error(e, "to get point data")
        return None