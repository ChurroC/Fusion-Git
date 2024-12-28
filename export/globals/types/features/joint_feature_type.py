from typing import Literal, TypedDict
from ..utils_type import Error, Point3D


# Joint Motion Types in Fusion 360
class JointMotion(TypedDict):
    type: Literal[0, 1, 2, 3, 4, 5]  # Rigid=0, Revolute=1, Slider=2, Cylindrical=3, Pin-Slot=4, Planar=5
    rotationAxis: Point3D
    rotationLimits: bool
    minRotationLimit: str  # "-180 deg"
    maxRotationLimit: str  # "180 deg"
    translationAxis: Point3D
    translationLimits: bool
    minTranslationLimit: str  # "-1 in"
    maxTranslationLimit: str  # "1 in"


# Joint Origin Types - How the joint is defined
class JointOrigin(TypedDict):
    type: Literal["geometry", "joint"]  # Whether joint is created from geometry or another joint
    geometry_or_joint_index: int  # Timeline index of the referenced geometry or joint


# Main Joint Details
class JointDetails(TypedDict):
    motion: JointMotion | Error
    origin: JointOrigin | Error
    is_flipped: bool  # Whether joint direction is flipped
    offset: Point3D  # Joint offset from origin
    angle: str  # "0 deg"


# Main Joint Feature (follows pattern of other features)
class JointFeature(TypedDict):
    name: str
    type: Literal["adsk::fusion::Joint"]
    details: JointDetails | Error
