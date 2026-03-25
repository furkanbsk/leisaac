from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RobotJointProfile:
    """Robot-specific joint metadata used by teleop and dataset conversion."""

    name: str
    single_arm_joint_names: tuple[str, ...]
    usd_joint_limits_deg: dict[str, tuple[float, float]]
    dataset_joint_limits: dict[str, tuple[float, float]]
    rest_pose_range_deg: dict[str, tuple[float, float]]
    ee_body_name: str
    gripper_joint_name: str
    robot_name: str

    @property
    def single_arm_dim(self) -> int:
        return len(self.single_arm_joint_names)

    @property
    def default_feature_joint_names(self) -> list[str]:
        return [f"{joint_name}.pos" for joint_name in self.single_arm_joint_names]

    @property
    def bi_arm_feature_joint_names(self) -> list[str]:
        return (
            [f"left_{joint_name}.pos" for joint_name in self.single_arm_joint_names]
            + [f"right_{joint_name}.pos" for joint_name in self.single_arm_joint_names]
        )


SO101_JOINT_PROFILE = RobotJointProfile(
    name="so101",
    single_arm_joint_names=("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"),
    usd_joint_limits_deg={
        "shoulder_pan": (-110.0, 110.0),
        "shoulder_lift": (-100.0, 100.0),
        "elbow_flex": (-100.0, 90.0),
        "wrist_flex": (-95.0, 95.0),
        "wrist_roll": (-160.0, 160.0),
        "gripper": (-10.0, 100.0),
    },
    dataset_joint_limits={
        "shoulder_pan": (-100.0, 100.0),
        "shoulder_lift": (-100.0, 100.0),
        "elbow_flex": (-100.0, 100.0),
        "wrist_flex": (-100.0, 100.0),
        "wrist_roll": (-100.0, 100.0),
        "gripper": (0.0, 100.0),
    },
    rest_pose_range_deg={
        "shoulder_pan": (-30.0, 30.0),
        "shoulder_lift": (-130.0, -70.0),
        "elbow_flex": (60.0, 120.0),
        "wrist_flex": (20.0, 80.0),
        "wrist_roll": (-30.0, 30.0),
        "gripper": (-40.0, 20.0),
    },
    ee_body_name="gripper",
    gripper_joint_name="gripper",
    robot_name="so101_follower",
)

LEKIWI_ARM_JOINT_PROFILE = RobotJointProfile(
    name="lekiwi_arm",
    single_arm_joint_names=SO101_JOINT_PROFILE.single_arm_joint_names,
    usd_joint_limits_deg=SO101_JOINT_PROFILE.usd_joint_limits_deg,
    dataset_joint_limits=SO101_JOINT_PROFILE.dataset_joint_limits,
    rest_pose_range_deg=SO101_JOINT_PROFILE.rest_pose_range_deg,
    ee_body_name="gripper",
    gripper_joint_name="gripper",
    robot_name="lekiwi",
)

FRANKA_JOINT_PROFILE = RobotJointProfile(
    name="franka",
    single_arm_joint_names=(
        "panda_joint1",
        "panda_joint2",
        "panda_joint3",
        "panda_joint4",
        "panda_joint5",
        "panda_joint6",
        "panda_joint7",
        "panda_finger_joint1",
    ),
    usd_joint_limits_deg={
        "panda_joint1": (-166.0, 166.0),
        "panda_joint2": (-101.0, 101.0),
        "panda_joint3": (-166.0, 166.0),
        "panda_joint4": (-176.0, -4.0),
        "panda_joint5": (-166.0, 166.0),
        "panda_joint6": (-1.0, 215.0),
        "panda_joint7": (-166.0, 166.0),
        "panda_finger_joint1": (0.0, 4.0),
    },
    dataset_joint_limits={
        "panda_joint1": (-166.0, 166.0),
        "panda_joint2": (-101.0, 101.0),
        "panda_joint3": (-166.0, 166.0),
        "panda_joint4": (-176.0, -4.0),
        "panda_joint5": (-166.0, 166.0),
        "panda_joint6": (-1.0, 215.0),
        "panda_joint7": (-166.0, 166.0),
        "panda_finger_joint1": (0.0, 4.0),
    },
    rest_pose_range_deg={
        "panda_joint1": (-20.0, 20.0),
        "panda_joint2": (-60.0, -20.0),
        "panda_joint3": (-20.0, 20.0),
        "panda_joint4": (-160.0, -120.0),
        "panda_joint5": (-20.0, 20.0),
        "panda_joint6": (80.0, 120.0),
        "panda_joint7": (-20.0, 20.0),
        "panda_finger_joint1": (0.0, 4.0),
    },
    ee_body_name="panda_hand",
    gripper_joint_name="panda_finger_joint1",
    robot_name="franka",
)


ROBOT_JOINT_PROFILES = {
    profile.name: profile
    for profile in (
        SO101_JOINT_PROFILE,
        LEKIWI_ARM_JOINT_PROFILE,
        FRANKA_JOINT_PROFILE,
    )
}


def get_robot_joint_profile(profile_name: str) -> RobotJointProfile:
    try:
        return ROBOT_JOINT_PROFILES[profile_name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown robot joint profile '{profile_name}'. Available: {sorted(ROBOT_JOINT_PROFILES.keys())}"
        ) from exc
