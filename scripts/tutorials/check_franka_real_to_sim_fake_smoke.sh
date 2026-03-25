#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROS_DISTRO="${ROS_DISTRO:-humble}"
ROS_WS="${ROS_WS:-$HOME/franka_ros2_ws}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/${ROS_DISTRO}/setup.bash}"
ROS_LAUNCH_LOG="$(mktemp)"
ISAACLAB_ROOT="${ISAACLAB_ROOT:-$HOME/IsaacLab}"
CONDA_ENV_NAME="${CONDA_ENV_NAME:-env_isaacsim}"
CONDA_SH="${CONDA_SH:-$HOME/miniconda3/etc/profile.d/conda.sh}"
ISAACSIM_ROOT="${ISAACSIM_ROOT:-$HOME/isaacsim}"

cleanup() {
  if [[ -n "${ROS_LAUNCH_PID:-}" ]] && kill -0 "${ROS_LAUNCH_PID}" 2>/dev/null; then
    kill "${ROS_LAUNCH_PID}" 2>/dev/null || true
    wait "${ROS_LAUNCH_PID}" 2>/dev/null || true
  fi
  rm -f "${ROS_LAUNCH_LOG}"
}
trap cleanup EXIT

source "${CONDA_SH}"
conda activate "${CONDA_ENV_NAME}"
set +u
source "${ISAACSIM_ROOT}/setup_conda_env.sh"
source "${ROS_SETUP}"
source "${ROS_WS}/install/setup.bash"
set -u

ros2 launch franka_bringup franka.launch.py \
  robot_type:=fr3 \
  use_fake_hardware:=true \
  load_gripper:=true \
  joint_state_rate:=30 >"${ROS_LAUNCH_LOG}" 2>&1 &
ROS_LAUNCH_PID=$!

for _ in $(seq 1 30); do
  if ros2 topic list | grep -qx '/joint_states'; then
    break
  fi
  sleep 1
done

if ! ros2 topic list | grep -qx '/joint_states'; then
  echo "[error] /joint_states did not appear. Launch log:"
  cat "${ROS_LAUNCH_LOG}"
  exit 1
fi

echo "[info] fake hardware publishing /joint_states"
timeout 5 ros2 topic echo /joint_states --once

cd "${ROOT_DIR}"
"${ISAACLAB_ROOT}/isaaclab.sh" -p scripts/tutorials/check_franka_leader_smoke.py --headless --enable_cameras --joint_state_topic /joint_states
