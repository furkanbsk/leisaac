#!/usr/bin/env python3

"""Headless smoke test for the Franka LiftCube task."""

import multiprocessing
import sys
import traceback
from pathlib import Path

if multiprocessing.get_start_method() != "spawn":
    multiprocessing.set_start_method("spawn", force=True)

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "source" / "leisaac"))

import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Smoke test the LeIsaac Franka LiftCube task.")
parser.add_argument("--task", type=str, default="LeIsaac-Franka-LiftCube-v0")
parser.add_argument("--teleop_device", type=str, default="franka-keyboard")
parser.add_argument("--num_envs", type=int, default=1)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
from gymnasium.spaces import flatdim
from isaaclab_tasks.utils import parse_env_cfg

import leisaac  # noqa: F401


def main():
    print("smoke_stage", "parse_env_cfg", flush=True)
    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs)
    env_cfg.use_teleop_device(args_cli.teleop_device)
    env_cfg.recorders = None
    env_cfg.seed = 0
    print("smoke_stage", "gym_make", flush=True)
    env = gym.make(args_cli.task, cfg=env_cfg).unwrapped

    try:
        print("smoke_stage", "reset", flush=True)
        env.reset()
        action_dim = flatdim(env.action_space)
        action = torch.zeros((env.num_envs, action_dim), device=env.device)
        print("smoke_stage", "step", flush=True)
        env.step(action)
        print(
            "smoke_ok",
            {
                "task": args_cli.task,
                "teleop_device": args_cli.teleop_device,
                "num_envs": env.num_envs,
                "action_dim": action_dim,
            },
            flush=True,
        )
    except BaseException as exc:
        print("smoke_error", type(exc).__name__, str(exc), flush=True)
        traceback.print_exc()
        raise
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
