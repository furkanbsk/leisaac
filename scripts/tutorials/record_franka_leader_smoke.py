#!/usr/bin/env python3

"""Record a tiny Franka leader-driven HDF5 dataset for smoke testing."""

import argparse
import multiprocessing
import sys
import time
from pathlib import Path

if multiprocessing.get_start_method() != "spawn":
    multiprocessing.set_start_method("spawn", force=True)

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "source" / "leisaac"))

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Record a tiny Franka leader-driven dataset.")
parser.add_argument("--task", type=str, default="LeIsaac-Franka-LiftCube-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--dataset_file", type=str, default=str(REPO_ROOT / "datasets" / "franka_leader_smoke.hdf5"))
parser.add_argument("--num_steps", type=int, default=8)
parser.add_argument("--joint_state_topic", type=str, default="/joint_states")
parser.add_argument("--state_timeout", type=float, default=1.0)
parser.add_argument("--wait_timeout", type=float, default=20.0)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
from isaaclab.managers import DatasetExportMode
from isaaclab.utils.datasets import HDF5DatasetFileHandler
from isaaclab_tasks.utils import parse_env_cfg

from leisaac.devices import FrankaLeader
from leisaac.enhance.managers import StreamingRecorderManager
import leisaac  # noqa: F401


def main():
    dataset_path = Path(args_cli.dataset_file)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    if dataset_path.exists():
        dataset_path.unlink()

    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs)
    env_cfg.use_teleop_device("franka-leader")
    env_cfg.seed = 0
    env_cfg.recorders.dataset_export_mode = DatasetExportMode.EXPORT_ALL
    env_cfg.recorders.dataset_export_dir_path = str(dataset_path.parent)
    env_cfg.recorders.dataset_filename = dataset_path.stem

    env = gym.make(args_cli.task, cfg=env_cfg).unwrapped
    del env.recorder_manager
    env.recorder_manager = StreamingRecorderManager(env_cfg.recorders, env)
    env.recorder_manager.flush_steps = 100
    env.recorder_manager.compression = "lzf"

    try:
        if hasattr(env, "initialize"):
            env.initialize()
        env.reset()

        teleop_interface = FrankaLeader(
            env,
            joint_state_topic=args_cli.joint_state_topic,
            state_timeout=args_cli.state_timeout,
        )

        deadline = time.time() + args_cli.wait_timeout
        action = None
        while time.time() < deadline:
            action = teleop_interface.advance()
            if action is not None:
                break
            env.sim.render()
            time.sleep(0.05)

        if action is None:
            raise RuntimeError(
                f"Timed out waiting for Franka leader action on topic {args_cli.joint_state_topic!r}."
            )

        for _ in range(args_cli.num_steps):
            next_action = teleop_interface.advance()
            if next_action is not None:
                action = next_action
            env.step(action)

        env.reset()
    finally:
        env.close()

    dataset_handler = HDF5DatasetFileHandler()
    dataset_handler.open(str(dataset_path))
    num_episodes = dataset_handler.get_num_episodes()
    print(
        "record_smoke_ok",
        {
            "dataset_file": str(dataset_path),
            "num_steps": args_cli.num_steps,
            "num_episodes": num_episodes,
        },
        flush=True,
    )
    simulation_app.close()


if __name__ == "__main__":
    main()
