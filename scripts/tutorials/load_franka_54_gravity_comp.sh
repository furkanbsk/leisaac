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

if ! ros2 node list 2>/dev/null | grep -qx "${CONTROLLER_MANAGER_NAME}"; then
    echo "controller_manager is not available at ${CONTROLLER_MANAGER_NAME}" >&2
    echo "Start the real robot bringup first." >&2
    exit 1
fi

exec ros2 run controller_manager spawner gravity_compensation_example_controller \
    --controller-manager "${CONTROLLER_MANAGER_NAME}"
