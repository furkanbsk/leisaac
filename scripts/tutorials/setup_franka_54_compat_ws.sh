#!/usr/bin/env bash

set -euo pipefail

FRANKA_ROS2_WS="${FRANKA_ROS2_WS:-$HOME/franka_ros2_54_ws}"
FRANKA_COMPAT_PREFIX="${FRANKA_COMPAT_PREFIX:-$HOME/franka_compat_prefix}"
FRANKA_ROBOT_IP="${FRANKA_ROBOT_IP:-172.16.0.2}"
FRANKA_ETH_IFACE="${FRANKA_ETH_IFACE:-enp4s0}"

echo "Setting up Franka compatibility workspace for system version 5.4.0"
echo "Workspace: ${FRANKA_ROS2_WS}"
echo "Prefix:    ${FRANKA_COMPAT_PREFIX}"

mkdir -p "${FRANKA_ROS2_WS}/src" "${FRANKA_COMPAT_PREFIX}" "${HOME}/build_logs"
cd "${FRANKA_ROS2_WS}/src"

rm -rf franka_ros2 libfranka

if ! git clone --branch v0.1.7 --depth 1 https://github.com/frankarobotics/franka_ros2.git; then
  git clone --branch v0.1.7 --depth 1 https://github.com/frankaemika/franka_ros2.git
fi

if ! git clone --branch 0.12.1 --depth 1 https://github.com/frankarobotics/libfranka.git; then
  git clone --branch 0.12.1 --depth 1 https://github.com/frankaemika/libfranka.git
fi

cd "${FRANKA_ROS2_WS}/src/libfranka"
git submodule update --init --recursive

sudo apt-get update -y >/dev/null
sudo apt-get install -y libpoco-dev libeigen3-dev ros-humble-generate-parameter-library >/dev/null

cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="${FRANKA_COMPAT_PREFIX}" \
  -DBUILD_TESTS=OFF \
  -DBUILD_EXAMPLES=OFF \
  > "${HOME}/build_logs/libfranka_configure.log" 2>&1

cmake --build build -j"$(nproc)" > "${HOME}/build_logs/libfranka_build.log" 2>&1
cmake --install build > "${HOME}/build_logs/libfranka_install.log" 2>&1

cd "${FRANKA_ROS2_WS}/src/franka_ros2"

# v0.1.7 expects older ros2_control include exports. Humble 2026 packages need this tiny patch.
perl -0pi -e 's/set\(THIS_PACKAGE_INCLUDE_DEPENDS Franka franka_hardware franka_msgs hardware_interface rclcpp_lifecycle\)/set(THIS_PACKAGE_INCLUDE_DEPENDS Franka franka_hardware franka_msgs hardware_interface rclcpp_lifecycle controller_interface)/g' \
  franka_semantic_components/CMakeLists.txt

cd "${FRANKA_ROS2_WS}"
source /opt/ros/humble/setup.bash
export CMAKE_PREFIX_PATH="${FRANKA_COMPAT_PREFIX}:${CMAKE_PREFIX_PATH:-}"
colcon build --symlink-install --cmake-args -DBUILD_TESTING=OFF > "${HOME}/build_logs/franka_ros2_54_build.log" 2>&1

sudo ufw allow in on "${FRANKA_ETH_IFACE}" from "${FRANKA_ROBOT_IP}" comment 'Franka FCI UDP' >/dev/null || true

cat <<EOF
Done.

Next steps:
  source /opt/ros/humble/setup.bash
  source "${FRANKA_ROS2_WS}/install/setup.bash"
  export LD_LIBRARY_PATH="${FRANKA_ROS2_WS}/install/libfranka/lib:${FRANKA_COMPAT_PREFIX}/lib:\${LD_LIBRARY_PATH:-}"
  ros2 launch franka_bringup franka.launch.py robot_type:=fr3 robot_ip:=${FRANKA_ROBOT_IP} load_gripper:=false use_fake_hardware:=false joint_state_rate:=30
EOF
