from typing import TypedDict, Union, get_origin, get_args, Literal, Generic, Type, Optional, Any, TypeVar, Tuple, Dict


class BaseTypedDict(TypedDict):
    pass


T = TypeVar("T", bound=Type[BaseTypedDict])


def get_matching_type(
    value: Dict[str, Any],
    possible_types: Tuple[Type[Any], ...],
) -> Optional[Type[BaseTypedDict]]:
    """Find matching TypedDict based on value structure"""
    if not isinstance(value, dict):
        return None

    # For Feature unions that have a 'type' field
    if "type" in value:
        for possible_type in possible_types:
            if isinstance(possible_type, type) and is_typeddict(possible_type):
                # Check if this TypedDict has matching 'type' field constraints
                try:
                    type_annotation = possible_type.__annotations__.get("type")
                    if is_literal(type_annotation):
                        literal_values = get_args(type_annotation)
                        if value["type"] in literal_values:
                            return possible_type
                except AttributeError:
                    continue

    # Default to first TypedDict in union if no match found
    for t in possible_types:
        if isinstance(t, type) and is_typeddict(t):
            return t

    return None


def is_literal(tp: Any) -> bool:
    """Check if a type is a Literal"""
    if tp is None:
        return False
    return get_origin(tp) is Literal


def is_typeddict(tp: Any) -> bool:
    """Check if a type is a TypedDict"""
    if not isinstance(tp, type):
        return False
    return hasattr(tp, "__annotations__") and hasattr(tp, "__total__")


def is_union(tp: Type[Any]) -> bool:
    """Check if a type is a Union"""
    return get_origin(tp) is Union


def order_dict(data: Dict[str, Any], schema: T) -> Dict[str, Any]:
    """Convert a dict to match TypedDict structure while maintaining key order"""
    if not isinstance(data, dict):
        return data

    result: Dict[str, Any] = {}

    for key, expected_type in schema.__annotations__.items():
        if key not in data:
            continue

        value = data[key]

        # Handle None values
        if value is None:
            result[key] = None
            continue

        # Get the actual type (handling Generic types)
        actual_type = get_origin(expected_type) or expected_type

        # Handle Lists
        if actual_type is list:
            element_type = get_args(expected_type)[0]
            if is_union(element_type):
                # Handle union types in lists (like list[Feature | Error])
                result[key] = [
                    dump_typed_dict(item, matching_type)
                    for item in value
                    if (matching_type := get_matching_type(item, get_args(element_type))) is not None
                ]
            elif is_typeddict(element_type):
                result[key] = [dump_typed_dict(item, element_type) for item in value]
            else:
                result[key] = value
            continue

        # Handle Unions (like Feature = SketchFeature | ExtrudeFeature)
        if is_union(actual_type):
            union_types = get_args(expected_type)
            matching_type = get_matching_type(value, union_types)
            if matching_type:
                result[key] = dump_typed_dict(value, matching_type)
            else:
                result[key] = value
            continue

        # Handle nested TypedDicts
        if is_typeddict(actual_type):
            result[key] = dump_typed_dict(value, actual_type)
            continue

        # Handle everything else (including Literals)
        result[key] = value

    return result
