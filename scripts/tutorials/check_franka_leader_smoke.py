#!/usr/bin/env python3

"""Headless smoke test for real-to-sim Franka leader actions."""

import argparse
import multiprocessing
import sys
import time
import traceback
from pathlib import Path

if multiprocessing.get_start_method() != "spawn":
    multiprocessing.set_start_method("spawn", force=True)

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "source" / "leisaac"))

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Smoke test the Franka real-to-sim leader path.")
parser.add_argument("--task", type=str, default="LeIsaac-Franka-LiftCube-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--joint_state_topic", type=str, default="/joint_states")
parser.add_argument("--state_timeout", type=float, default=1.0)
parser.add_argument("--wait_timeout", type=float, default=10.0)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
from isaaclab_tasks.utils import parse_env_cfg

from leisaac.devices import FrankaLeader
import leisaac  # noqa: F401


def main():
    print("leader_smoke_stage", "parse_env_cfg", flush=True)
    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs)
    env_cfg.use_teleop_device("franka-leader")
    env_cfg.recorders = None
    env_cfg.seed = 0

    print("leader_smoke_stage", "gym_make", flush=True)
    env = gym.make(args_cli.task, cfg=env_cfg).unwrapped

    try:
        if hasattr(env, "initialize"):
            env.initialize()
        print("leader_smoke_stage", "reset", flush=True)
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

        print("leader_smoke_stage", "step", flush=True)
        env.step(action)
        print(
            "leader_smoke_ok",
            {
                "task": args_cli.task,
                "num_envs": env.num_envs,
                "joint_state_topic": args_cli.joint_state_topic,
                "action_shape": tuple(action.shape),
            },
            flush=True,
        )
    except BaseException as exc:
        print("leader_smoke_error", type(exc).__name__, str(exc), flush=True)
        traceback.print_exc()
        raise
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
