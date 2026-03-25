#!/usr/bin/env python3

"""Record a tiny Franka LiftCube HDF5 dataset for smoke testing."""

import multiprocessing
import sys
from pathlib import Path

if multiprocessing.get_start_method() != "spawn":
    multiprocessing.set_start_method("spawn", force=True)

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "source" / "leisaac"))

import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Record a tiny Franka LiftCube dataset.")
parser.add_argument("--task", type=str, default="LeIsaac-Franka-LiftCube-v0")
parser.add_argument("--teleop_device", type=str, default="franka-keyboard")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--dataset_file", type=str, default=str(REPO_ROOT / "datasets" / "franka_liftcube_smoke.hdf5"))
parser.add_argument("--num_steps", type=int, default=3)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
from gymnasium.spaces import flatdim
from isaaclab.managers import DatasetExportMode
from isaaclab_tasks.utils import parse_env_cfg
from leisaac.enhance.managers import StreamingRecorderManager

import leisaac  # noqa: F401


def main():
    dataset_path = Path(args_cli.dataset_file)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    if dataset_path.exists():
        dataset_path.unlink()

    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs)
    env_cfg.use_teleop_device(args_cli.teleop_device)
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
        env.reset()
        action_dim = flatdim(env.action_space)
        action = torch.zeros((env.num_envs, action_dim), device=env.device)
        for _ in range(args_cli.num_steps):
            env.step(action)
        env.reset()
        print(
            "record_smoke_ok",
            {
                "dataset_file": str(dataset_path),
                "num_steps": args_cli.num_steps,
            },
            flush=True,
        )
    finally:
        env.close()
        simulation_app.close()


if __name__ == "__main__":
    main()
