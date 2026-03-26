#!/usr/bin/env python3

"""Preview a single Lightwheel USD asset in Isaac Sim."""

import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Preview a single Lightwheel asset.")
parser.add_argument("--usd_path", type=str, required=True, help="Absolute path to the USD asset to preview.")
parser.add_argument("--asset_height", type=float, default=0.02, help="Spawn height of the asset.")
parser.add_argument("--scale", type=float, default=1.0, help="Uniform asset scale.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sim import SimulationContext
from isaaclab.utils import configclass


@configclass
class PreviewSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(prim_path="/World/defaultGroundPlane", spawn=sim_utils.GroundPlaneCfg())
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.9, 0.9, 0.9)),
    )
    asset = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/PreviewAsset",
        spawn=sim_utils.UsdFileCfg(usd_path="", scale=(1.0, 1.0, 1.0)),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, 0.02)),
    )


def main():
    sim_cfg = sim_utils.SimulationCfg(device=args_cli.device)
    sim = SimulationContext(sim_cfg)
    sim.set_camera_view([1.2, 1.2, 0.8], [0.0, 0.0, 0.15])

    scene_cfg = PreviewSceneCfg(num_envs=1, env_spacing=1.0)
    scene_cfg.asset.spawn.usd_path = args_cli.usd_path
    scene_cfg.asset.spawn.scale = (args_cli.scale, args_cli.scale, args_cli.scale)
    scene_cfg.asset.init_state.pos = (0.0, 0.0, args_cli.asset_height)
    scene = InteractiveScene(scene_cfg)

    sim.reset()
    print("[INFO]: Asset preview ready...", flush=True)

    sim_dt = sim.get_physics_dt()
    while simulation_app.is_running():
        scene.write_data_to_sim()
        sim.step()
        scene.update(sim_dt)


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
