#!/usr/bin/env bash
set -euo pipefail

TASK="${1:-LeIsaac-Franka-BowlCubeZone-v0}"
TELEOP_DEVICE="${TELEOP_DEVICE:-franka-leader}"
NUM_ENVS="${NUM_ENVS:-1}"
RENDERING_MODE="${RENDERING_MODE:-performance}"

export DISPLAY="${DISPLAY:-:0}"
export XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/1000}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/1000/bus}"
export AMENT_TRACE_SETUP_FILES="${AMENT_TRACE_SETUP_FILES-}"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate env_isaacsim

if [ -f "$HOME/isaacsim/setup_conda_env.sh" ]; then
    source "$HOME/isaacsim/setup_conda_env.sh"
fi

set +u
source /opt/ros/humble/setup.bash
source "$HOME/franka_ros2_54_ws/install/setup.bash"
set -u
export LD_LIBRARY_PATH="$HOME/franka_ros2_54_ws/install/libfranka/lib:$HOME/franka_compat_prefix/lib:${LD_LIBRARY_PATH:-}"

cd "$HOME/furkan_workspace/leisaac"

"$HOME/IsaacLab/isaaclab.sh" -p scripts/environments/teleoperation/teleop_se3_agent.py \
    --task "$TASK" \
    --teleop_device "$TELEOP_DEVICE" \
    --num_envs "$NUM_ENVS" \
    --rendering_mode "$RENDERING_MODE"
