#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROS_DISTRO="${ROS_DISTRO:-humble}"
CONDA_ENV_NAME="${CONDA_ENV_NAME:-env_isaacsim}"
CONDA_SH="${CONDA_SH:-$HOME/miniconda3/etc/profile.d/conda.sh}"
ISAACSIM_ROOT="${ISAACSIM_ROOT:-$HOME/isaacsim}"
ISAACLAB_ROOT="${ISAACLAB_ROOT:-$HOME/IsaacLab}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/${ROS_DISTRO}/setup.bash}"
ROS_WS="${ROS_WS:-$HOME/franka_ros2_ws}"

print_section() {
    printf '\n== %s ==\n' "$1"
}

print_status() {
    local label="$1"
    local path="$2"
    if [[ -e "$path" ]]; then
        printf '[ok] %s: %s\n' "$label" "$path"
    else
        printf '[missing] %s: %s\n' "$label" "$path"
    fi
}

print_section "Chosen Paths"
printf 'repo_root: %s\n' "$ROOT_DIR"
printf 'conda_env_name: %s\n' "$CONDA_ENV_NAME"
printf 'ros_distro: %s\n' "$ROS_DISTRO"
printf 'conda_sh: %s\n' "$CONDA_SH"
printf 'isaacsim_root: %s\n' "$ISAACSIM_ROOT"
printf 'isaaclab_root: %s\n' "$ISAACLAB_ROOT"
printf 'ros_setup: %s\n' "$ROS_SETUP"
printf 'ros_ws: %s\n' "$ROS_WS"

print_section "Filesystem Checks"
print_status "conda init script" "$CONDA_SH"
print_status "Isaac Sim root" "$ISAACSIM_ROOT"
print_status "Isaac Sim conda env script" "$ISAACSIM_ROOT/setup_conda_env.sh"
print_status "IsaacLab root" "$ISAACLAB_ROOT"
print_status "IsaacLab launcher" "$ISAACLAB_ROOT/isaaclab.sh"
print_status "ROS setup" "$ROS_SETUP"
print_status "franka_ros2 workspace" "$ROS_WS"
print_status "franka_ros2 install setup" "$ROS_WS/install/setup.bash"
print_status "scene asset" "$ROOT_DIR/assets/scenes/table_with_cube/scene.usd"

print_section "Python and ROS Checks"
if [[ -f "$CONDA_SH" ]]; then
    source "$CONDA_SH"
    conda activate "$CONDA_ENV_NAME"
    set +u
    if [[ -f "$ISAACSIM_ROOT/setup_conda_env.sh" ]]; then
        source "$ISAACSIM_ROOT/setup_conda_env.sh"
    fi
    set -u
    python - <<'PY'
import importlib.util
mods = ["isaaclab", "isaaclab_tasks", "rclpy", "sensor_msgs.msg"]
for mod in mods:
    print(f"{mod}: {'ok' if importlib.util.find_spec(mod) else 'missing'}")
PY
fi

if [[ -f "$ROS_SETUP" ]]; then
    set +u
    source "$ROS_SETUP"
    if [[ -f "$ROS_WS/install/setup.bash" ]]; then
        source "$ROS_WS/install/setup.bash"
    fi
    set -u
    ros2 pkg list | rg '^franka' || true
fi

print_section "Compatibility Notes"
cat <<'EOF'
- The helper scripts now resolve external dependencies through env vars first.
- `isaaclab` and `isaaclab_tasks` may show as missing in plain Python checks.
  The canonical runtime check is whether `$ISAACLAB_ROOT/isaaclab.sh` exists and the smoke scripts run.
- If your new machine uses different install locations, override:
  CONDA_SH, CONDA_ENV_NAME, ISAACSIM_ROOT, ISAACLAB_ROOT, ROS_SETUP, ROS_WS, ROS_DISTRO
- The local Isaac Sim compatibility shim may still need to exist at:
  $ISAACSIM_ROOT/__init__.py
EOF
