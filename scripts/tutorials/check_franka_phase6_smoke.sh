#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ASSET_ROOT="${LEISAAC_ASSETS_ROOT:-$REPO_ROOT/assets}"
TABLE_WITH_CUBE_SCENE="$ASSET_ROOT/scenes/table_with_cube/scene.usd"
ISAACLAB_ROOT="${ISAACLAB_ROOT:-$HOME/IsaacLab}"
CONDA_ENV_NAME="${CONDA_ENV_NAME:-env_isaacsim}"
CONDA_SH="${CONDA_SH:-$HOME/miniconda3/etc/profile.d/conda.sh}"
ISAACSIM_ROOT="${ISAACSIM_ROOT:-$HOME/isaacsim}"

print_section() {
    printf '\n== %s ==\n' "$1"
}

print_section "Franka Smoke"
printf 'repo_root: %s\n' "$REPO_ROOT"
printf 'asset_root: %s\n' "$ASSET_ROOT"

print_section "Asset Check"
if [ -f "$TABLE_WITH_CUBE_SCENE" ]; then
    printf '[ok] table_with_cube scene found: %s\n' "$TABLE_WITH_CUBE_SCENE"
else
    printf '[missing] required scene asset not found: %s\n' "$TABLE_WITH_CUBE_SCENE"
fi

print_section "Runtime Smoke"
set +e
source "$CONDA_SH"
conda activate "$CONDA_ENV_NAME"
set +u
source "$ISAACSIM_ROOT/setup_conda_env.sh"
set -u
cd "$REPO_ROOT"
"$ISAACLAB_ROOT/isaaclab.sh" -p scripts/tutorials/check_franka_liftcube_smoke.py --headless \
    --enable_cameras \
    > /tmp/leisaac_franka_smoke_runtime.log 2>&1
status=$?
set -e
cat /tmp/leisaac_franka_smoke_runtime.log
printf 'runtime_exit_code: %s\n' "$status"
smoke_ok=0
if grep -q "smoke_ok" /tmp/leisaac_franka_smoke_runtime.log; then
    smoke_ok=1
fi
printf 'smoke_ok_marker: %s\n' "$smoke_ok"

print_section "Smoke Summary"
if [ ! -f "$TABLE_WITH_CUBE_SCENE" ]; then
    printf '[blocked] runtime smoke test cannot proceed until the table_with_cube scene asset is installed.\n'
fi
if [ "$status" -ne 0 ] || [ "$smoke_ok" -ne 1 ]; then
    printf '[blocked] runtime smoke test failed during Isaac app launch or env creation.\n'
fi
if [ -f "$TABLE_WITH_CUBE_SCENE" ] && [ "$status" -eq 0 ] && [ "$smoke_ok" -eq 1 ]; then
    printf '[ready] environment is ready for teleop/record/replay smoke testing.\n'
fi
