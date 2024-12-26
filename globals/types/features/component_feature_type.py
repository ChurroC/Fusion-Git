from typing import Literal, TypedDict
from ..utils_type import Error

class ComponentDetails(TypedDict):
    is_linked: bool
    id: str
    # source_file: NotRequired[str] - maybe add

class ComponentFeature(TypedDict):
    name: str
    type: Literal["adsk::fusion::Occurrence"]
    details: ComponentDetails | Error
