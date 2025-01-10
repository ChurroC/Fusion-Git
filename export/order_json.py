from typing import Mapping, TypedDict, Dict, Any, Type, TypeVar, get_origin, get_args, cast


class BaseTypedDict(TypedDict):
    pass


T = TypeVar("T", bound=BaseTypedDict)


def order_dict(data: Mapping, schema: Type[T]) -> T:
    """
    Orders a dictionary's keys according to a TypedDict's structure

    Args:
        data: Dictionary to order (must match schema type)
        schema: TypedDict class to use as template

    Returns:
        New dictionary with keys ordered according to schema
    """
    if not isinstance(data, Mapping):
        return data

    result: Dict[str, Any] = {}

    # Process each field in the schema's order
    for key, expected_type in schema.__annotations__.items():
        if key not in data:
            continue

        value = data[key]

        # Handle None values
        if value is None:
            result[key] = None
            continue

        # Get base type, handling generic types
        base_type = get_origin(expected_type) or expected_type

        # Handle nested dictionaries
        if isinstance(value, dict) and hasattr(base_type, "__annotations__"):
            result[key] = order_dict(value, base_type)
            continue

        # Handle lists of dictionaries
        if isinstance(value, list) and base_type is list:
            type_args = get_args(expected_type)
            if type_args and hasattr(type_args[0], "__annotations__"):
                result[key] = [order_dict(item, type_args[0]) for item in value]
            else:
                result[key] = value
            continue

        # For all other types, keep the value as is
        result[key] = value

    return cast(T, result)
