#!/usr/bin/env bash
set -euo pipefail

FRANKA_ROS2_WS="${FRANKA_ROS2_WS:-$HOME/franka_ros2_54_ws}"
FRANKA_COMPAT_PREFIX="${FRANKA_COMPAT_PREFIX:-$HOME/franka_compat_prefix}"
CONTROLLER_MANAGER_NAME="${CONTROLLER_MANAGER_NAME:-/controller_manager}"

export AMENT_TRACE_SETUP_FILES="${AMENT_TRACE_SETUP_FILES-}"
set +u
source /opt/ros/humble/setup.bash
source "${FRANKA_ROS2_WS}/install/setup.bash"
set -u
export LD_LIBRARY_PATH="${FRANKA_ROS2_WS}/install/libfranka/lib:${FRANKA_COMPAT_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

exec ros2 run controller_manager unspawner gravity_compensation_example_controller \
    --controller-manager "${CONTROLLER_MANAGER_NAME}"
