from dataclasses import MISSING
from typing import Any

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab.sensors import FrameTransformerCfg, OffsetCfg, TiledCameraCfg
from isaaclab.utils import configclass
from leisaac.assets.robots.franka import FRANKA_PANDA_HIGH_PD_CFG
from leisaac.devices.action_process import init_action_cfg
from leisaac.tasks.template.direct.single_arm_env import SingleArmTaskDirectEnvCfg
from leisaac.utils.robot_profiles import FRANKA_JOINT_PROFILE

from .single_arm_env_cfg import SingleArmTaskEnvCfg, SingleArmTaskSceneCfg


@configclass
class FrankaSingleArmTaskSceneCfg(SingleArmTaskSceneCfg):
    """Single-arm template scene configured for Franka Panda."""

    robot: ArticulationCfg = FRANKA_PANDA_HIGH_PD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

    ee_frame: FrameTransformerCfg = FrameTransformerCfg(
        prim_path="{ENV_REGEX_NS}/Robot/panda_link0",
        debug_vis=False,
        target_frames=[
            FrameTransformerCfg.FrameCfg(
                prim_path="{ENV_REGEX_NS}/Robot/panda_hand",
                name="gripper",
            ),
            FrameTransformerCfg.FrameCfg(
                prim_path="{ENV_REGEX_NS}/Robot/panda_hand",
                name="jaw",
                offset=OffsetCfg(pos=(0.0, 0.0, 0.107)),
            ),
        ],
    )

    wrist: TiledCameraCfg = TiledCameraCfg(
        prim_path="{ENV_REGEX_NS}/Robot/panda_hand/wrist_camera",
        offset=TiledCameraCfg.OffsetCfg(
            pos=(0.02, 0.0, -0.02),
            rot=(0.70711, 0.0, 0.70711, 0.0),
            convention="ros",
        ),
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=36.5,
            focus_distance=400.0,
            horizontal_aperture=36.83,
            clipping_range=(0.01, 50.0),
            lock_camera=True,
        ),
        width=640,
        height=480,
        update_period=1 / 30.0,
    )

    front: TiledCameraCfg = TiledCameraCfg(
        prim_path="{ENV_REGEX_NS}/Robot/panda_link0/front_camera",
        offset=TiledCameraCfg.OffsetCfg(
            pos=(0.0, -0.55, 0.5),
            rot=(0.18301, -0.96593, 0.0, 0.18301),
            convention="ros",
        ),
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=28.7,
            focus_distance=400.0,
            horizontal_aperture=38.11,
            clipping_range=(0.01, 50.0),
            lock_camera=True,
        ),
        width=640,
        height=480,
        update_period=1 / 30.0,
    )


@configclass
class FrankaSingleArmTaskEnvCfg(SingleArmTaskEnvCfg):
    """Single-arm template env configured for Franka Panda."""

    scene: FrankaSingleArmTaskSceneCfg = MISSING
    robot_name: str = FRANKA_JOINT_PROFILE.robot_name
    joint_profile_name: str = FRANKA_JOINT_PROFILE.name

    def __post_init__(self) -> None:
        super().__post_init__()
        self.viewer.eye = (1.2, -1.0, 0.9)
        self.viewer.lookat = (0.4, -0.1, 0.3)
        self.scene.robot.init_state.pos = (0.35, -0.64, 0.0)

    def use_teleop_device(self, teleop_device: str) -> None:
        self.task_type = teleop_device
        if teleop_device not in ["franka-keyboard", "franka-spacemouse", "franka-leader"]:
            raise ValueError(
                "FrankaSingleArmTaskEnvCfg only supports 'franka-keyboard', 'franka-spacemouse', and 'franka-leader'."
            )
        self.actions = init_action_cfg(self.actions, device=teleop_device)
        self.scene.robot.spawn.rigid_props.disable_gravity = True


@configclass
class FrankaSingleArmTaskDirectEnvCfg(SingleArmTaskDirectEnvCfg):
    """Direct single-arm template env configured for Franka Panda."""

    scene: FrankaSingleArmTaskSceneCfg = MISSING
    robot_name: str = FRANKA_JOINT_PROFILE.robot_name
    joint_profile_name: str = FRANKA_JOINT_PROFILE.name

    def __post_init__(self) -> None:
        super().__post_init__()
        self.viewer.eye = (1.2, -1.0, 0.9)
        self.viewer.lookat = (0.4, -0.1, 0.3)
        self.scene.robot.init_state.pos = (0.35, -0.64, 0.0)

    def use_teleop_device(self, teleop_device: str) -> None:
        raise NotImplementedError(
            "Franka direct env teleop is not wired. Use the manager-based Franka env with "
            "'franka-keyboard' or 'franka-spacemouse'."
        )
