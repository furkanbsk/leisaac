#!/usr/bin/env bash

set -euo pipefail

FRANKA_ROS2_WS="${FRANKA_ROS2_WS:-$HOME/franka_ros2_54_ws}"
FRANKA_COMPAT_PREFIX="${FRANKA_COMPAT_PREFIX:-$HOME/franka_compat_prefix}"
FRANKA_ROBOT_IP="${FRANKA_ROBOT_IP:-172.16.0.2}"

source /opt/ros/humble/setup.bash
source "${FRANKA_ROS2_WS}/install/setup.bash"
export LD_LIBRARY_PATH="${FRANKA_ROS2_WS}/install/libfranka/lib:${FRANKA_COMPAT_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

exec ros2 launch franka_bringup franka.launch.py \
  robot_type:=fr3 \
  robot_ip:="${FRANKA_ROBOT_IP}" \
  load_gripper:=false \
  use_fake_hardware:=false \
  joint_state_rate:=30
