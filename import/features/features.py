from typing import Callable, Dict

from .sketch import set_sketch_data
from .extrude import set_extrude_data

FEATURE_HANDLER: Dict[str, Callable[..., None]] = {
    "adsk::fusion::Sketch": set_sketch_data,
    "adsk::fusion::ExtrudeFeature": set_extrude_data,
}
