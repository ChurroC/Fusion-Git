# from typing import Literal, cast
# import adsk.fusion
# from ..globals.types.types import Error, JointDetails, JointMotion, JointOrigin
# from ..globals.globals import error
# from ..globals.utils import get_point_data, format_value


# def get_joint_data(joint: adsk.fusion.Joint) -> JointDetails | Error:
#     """Process a Fusion 360 joint and extract its details"""
#     try:
#         data: JointDetails = {
#             "motion": get_joint_motion_data(joint),
#             "origin": get_joint_origin_data(joint),
#             "is_flipped": joint.isFlipped,
#             "offset": get_point_data(joint.geometryOrOriginOne.origin),
#             "angle": format_value(joint.angle),
#         }

#         return data
#     except Exception as e:
#         return error(f"Failed to process joint {joint.name}", e)


# def get_joint_motion_data(joint: adsk.fusion.Joint) -> JointMotion | Error:
#     """Extract motion data from a joint"""
#     try:
#         # Get joint motion object
#         motion = joint.jointMotion

#         motion_data: JointMotion = {
#             "type": cast(Literal[0, 1, 2, 3, 4, 5], motion.jointType),
#             "rotationAxis": get_point_data(motion.rotationAxis),
#             "rotationLimits": motion.rotationLimitsEnabled,
#             "minRotationLimit": format_value(motion.rotationLimitLow),
#             "maxRotationLimit": format_value(motion.rotationLimitHigh),
#             "translationAxis": get_point_data(motion.slideDirection),
#             "translationLimits": motion.slideLimitsEnabled,
#             "minTranslationLimit": format_value(motion.slideLimitLow),
#             "maxTranslationLimit": format_value(motion.slideLimitHigh),
#         }

#         return motion_data
#     except Exception as e:
#         return error("Failed to process joint motion", e)


# def get_joint_origin_data(joint: adsk.fusion.Joint) -> JointOrigin | Error:
#     """Determine how the joint is defined (from geometry or another joint)"""
#     try:
#         if joint.geometryOrOriginOne.objectType == adsk.fusion.JointGeometry.classType():
#             origin_data: JointOrigin = {
#                 "type": "geometry",
#                 "geometry_or_joint_index": joint.geometryOrOriginOne.timelineObject.index,
#             }
#         else:
#             origin_data: JointOrigin = {
#                 "type": "joint",
#                 "geometry_or_joint_index": joint.geometryOrOriginOne.timelineObject.index,
#             }

#         return origin_data
#     except Exception as e:
#         return error("Failed to process joint origin", e)
