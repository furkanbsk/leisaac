import os
from pathlib import Path

from .robot_profiles import LEKIWI_ARM_JOINT_PROFILE, SO101_JOINT_PROFILE


def _detect_git_root() -> Path:
    """Locate repository root; fallback to current file ancestor."""
    try:
        from git import Repo

        repo = Repo(os.getcwd(), search_parent_directories=True)
        return Path(repo.git.rev_parse("--show-toplevel"))
    except Exception:
        return Path(__file__).resolve().parents[4]


def _resolve_assets_root() -> str:
    """Return env override if provided, otherwise default assets directory."""
    env_root = os.environ.get("LEISAAC_ASSETS_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve().as_posix()

    return (_detect_git_root() / "assets").resolve().as_posix()


ASSETS_ROOT = _resolve_assets_root()

SINGLE_ARM_JOINT_NAMES = list(SO101_JOINT_PROFILE.single_arm_joint_names)
BI_ARM_JOINT_NAMES = [
    *[f"left_{joint_name}" for joint_name in SO101_JOINT_PROFILE.single_arm_joint_names],
    *[f"right_{joint_name}" for joint_name in SO101_JOINT_PROFILE.single_arm_joint_names],
]
LEKIWI_JOINT_NAMES = [
    *LEKIWI_ARM_JOINT_PROFILE.single_arm_joint_names,
    "x",
    "y",
    "theta",
]
