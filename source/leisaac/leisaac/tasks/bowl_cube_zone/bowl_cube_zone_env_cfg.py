from pathlib import Path

from isaaclab.assets import AssetBaseCfg
from isaaclab.sim.spawners.from_files.from_files_cfg import UsdFileCfg
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR
from isaaclab_tasks.manager_based.manipulation.lift import lift_env_cfg
from isaaclab_tasks.manager_based.manipulation.lift.config.franka import ik_rel_env_cfg

from leisaac.devices.action_process import init_action_cfg, preprocess_device_action


REPO_ROOT = Path(__file__).resolve().parents[5]
PLATE_USD_PATH = (
    REPO_ROOT
    / "assets/lightwheel_candidates/Lightwheel_OpenSource/Locomotion/KitchenRoom/Kitchen_Other/Kitchen_Disk002.usd"
)
PLATE_POS = (0.62, -0.18, 0.02)
PLATE_ROT = (1.0, 0.0, 0.0, 0.0)
PLATE_SCALE = (1.0, 1.0, 1.0)

MARKING_POS = (0.60, -0.08, 0.001)
MARKING_ROT = (1.0, 0.0, 0.0, 0.0)
MARKING_SCALE = (0.14, 0.14, 0.14)


@configclass
class FrankaBowlCubeZoneSceneCfg(lift_env_cfg.ObjectTableSceneCfg):
    plate = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Plate",
        spawn=UsdFileCfg(
            usd_path=str(PLATE_USD_PATH),
            scale=PLATE_SCALE,
        ),
        init_state=AssetBaseCfg.InitialStateCfg(pos=PLATE_POS, rot=PLATE_ROT),
    )

    marking = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Marking",
        init_state=AssetBaseCfg.InitialStateCfg(pos=MARKING_POS, rot=MARKING_ROT),
        spawn=UsdFileCfg(
            usd_path=(
                f"{ISAAC_NUCLEUS_DIR}/Samples/Scene_Blox/Warehouse_Tiles/Props/MarkingLines/"
                "SM_MarkingLinesRectangle_A1_2x4_01.usd"
            ),
            scale=MARKING_SCALE,
        ),
    )


@configclass
class FrankaBowlCubeZoneEnvCfg(ik_rel_env_cfg.FrankaCubeLiftEnvCfg):
    """Teleop-compatible clone of the official Isaac Lift Cube Franka IK-Rel environment.

    This intentionally keeps the official Isaac Lab scene, robot placement, cube placement,
    table, commands, rewards, and terminations unchanged. Custom bowl/marking assets will be
    layered on top later.
    """

    scene: FrankaBowlCubeZoneSceneCfg = FrankaBowlCubeZoneSceneCfg(num_envs=4096, env_spacing=2.5)
    dynamic_reset_gripper_effort_limit: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.scene.object.init_state.pos = (0.56, 0.06, 0.025)
        self.commands.object_pose.debug_vis = False
        if hasattr(self.events, "reset_object_position"):
            self.events.reset_object_position = None

    def use_teleop_device(self, teleop_device: str) -> None:
        self.task_type = teleop_device
        if teleop_device not in ["franka-keyboard", "franka-spacemouse", "franka-leader"]:
            raise ValueError(
                "FrankaBowlCubeZoneEnvCfg only supports 'franka-keyboard', 'franka-spacemouse', and 'franka-leader'."
            )

        # The official IK-Rel config already matches keyboard/spacemouse usage.
        # We only override actions when a real Franka leader should mirror joint states.
        if teleop_device == "franka-leader":
            self.actions = init_action_cfg(self.actions, device=teleop_device)

    def preprocess_device_action(self, action, teleop_device):
        return preprocess_device_action(action, teleop_device)
