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
DATASET_FILE="${DATASET_FILE:-$ROOT_DIR/datasets/franka_leader_fake_smoke.hdf5}"
RECORD_LOG="$(mktemp)"
REPLAY_LOG="$(mktemp)"

cleanup_stale_isaac_processes() {
  pkill -9 -f "scripts/tutorials/check_franka_leader_smoke.py" 2>/dev/null || true
  pkill -9 -f "scripts/tutorials/record_franka_leader_smoke.py" 2>/dev/null || true
  pkill -9 -f "scripts/environments/teleoperation/replay.py" 2>/dev/null || true
  pkill -9 -f "/IsaacLab/isaaclab.sh -p scripts/tutorials/check_franka_leader_smoke.py" 2>/dev/null || true
  pkill -9 -f "/IsaacLab/isaaclab.sh -p scripts/tutorials/record_franka_leader_smoke.py" 2>/dev/null || true
  pkill -9 -f "/IsaacLab/isaaclab.sh -p scripts/environments/teleoperation/replay.py" 2>/dev/null || true
}

cleanup() {
  if [[ -n "${ROS_LAUNCH_PID:-}" ]] && kill -0 "${ROS_LAUNCH_PID}" 2>/dev/null; then
    kill "${ROS_LAUNCH_PID}" 2>/dev/null || true
  fi
  cleanup_stale_ros_processes
  cleanup_stale_isaac_processes
  rm -f "${ROS_LAUNCH_LOG}" "${RECORD_LOG}" "${REPLAY_LOG}"
}
trap cleanup EXIT

cleanup_stale_ros_processes() {
  pkill -9 -f "/opt/ros/humble/lib/controller_manager/ros2_control_node" 2>/dev/null || true
  pkill -9 -f "/opt/ros/humble/lib/robot_state_publisher/robot_state_publisher" 2>/dev/null || true
  pkill -9 -f "/opt/ros/humble/lib/joint_state_publisher/joint_state_publisher" 2>/dev/null || true
  pkill -9 -f "fake_gripper_state_publisher.py" 2>/dev/null || true
}

cleanup_stale_isaac_processes
cleanup_stale_ros_processes

set +u
source "${ROS_SETUP}"
source "${ROS_WS}/install/setup.bash"
set -u

setsid ros2 launch franka_bringup franka.launch.py \
  robot_type:=fr3 \
  use_fake_hardware:=true \
  load_gripper:=true \
  joint_state_rate:=30 >"${ROS_LAUNCH_LOG}" 2>&1 &
ROS_LAUNCH_PID=$!
disown "${ROS_LAUNCH_PID}" 2>/dev/null || true

sleep 8
echo "[info] fake hardware launch started; record/replay smoke will validate state reception"

export CONDA_NO_PLUGINS="${CONDA_NO_PLUGINS:-yes}"
source "${CONDA_SH}"
conda activate "${CONDA_ENV_NAME}"
set +u
if [[ -f "${ISAACSIM_ROOT}/setup_conda_env.sh" ]]; then
  source "${ISAACSIM_ROOT}/setup_conda_env.sh"
fi
source "${ROS_SETUP}"
source "${ROS_WS}/install/setup.bash"
set -u

rm -f "${DATASET_FILE}"
cd "${ROOT_DIR}"

if ! "${ISAACLAB_ROOT}/isaaclab.sh" -p scripts/tutorials/record_franka_leader_smoke.py \
  --headless \
  --enable_cameras \
  --dataset_file "${DATASET_FILE}" \
  >"${RECORD_LOG}" 2>&1; then
  cat "${RECORD_LOG}"
  echo "[error] record smoke failed. Launch log:"
  cat "${ROS_LAUNCH_LOG}"
  exit 1
fi

cat "${RECORD_LOG}"
if ! grep -q "record_smoke_ok" "${RECORD_LOG}"; then
  echo "[error] record smoke did not emit success marker."
  exit 1
fi

if [[ -n "${ROS_LAUNCH_PID:-}" ]] && kill -0 "${ROS_LAUNCH_PID}" 2>/dev/null; then
  kill "${ROS_LAUNCH_PID}" 2>/dev/null || true
fi
cleanup_stale_ros_processes
unset ROS_LAUNCH_PID

if ! "${ISAACLAB_ROOT}/isaaclab.sh" -p scripts/environments/teleoperation/replay.py \
  --headless \
  --enable_cameras \
  --task LeIsaac-Franka-LiftCube-v0 \
  --task_type franka-leader \
  --dataset_file "${DATASET_FILE}" \
  --replay_mode action \
  >"${REPLAY_LOG}" 2>&1; then
  cat "${REPLAY_LOG}"
  echo "[error] replay smoke failed. Launch log:"
  cat "${ROS_LAUNCH_LOG}"
  exit 1
fi

cat "${REPLAY_LOG}"
if ! grep -q "Finished replaying" "${REPLAY_LOG}"; then
  echo "[error] replay smoke did not emit completion marker."
  exit 1
fi

echo "record_replay_smoke_ok ${DATASET_FILE}"
