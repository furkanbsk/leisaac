#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

print_section() {
    printf '\n== %s ==\n' "$1"
}

print_path_status() {
    local label="$1"
    local path="$2"
    if [ -e "$path" ]; then
        printf '[ok] %s: %s\n' "$label" "$path"
    else
        printf '[missing] %s: %s\n' "$label" "$path"
    fi
}

print_section "Repo"
printf 'repo_root: %s\n' "$REPO_ROOT"
git -C "$REPO_ROOT" status --short --branch

print_section "Submodule"
git -C "$REPO_ROOT" submodule status
if [ -d "$REPO_ROOT/dependencies/IsaacLab/.git" ] || [ -f "$REPO_ROOT/dependencies/IsaacLab/.git" ]; then
    printf 'leisaac_pinned_isaaclab: '
    git -C "$REPO_ROOT/dependencies/IsaacLab" describe --tags --always
else
    printf '[missing] dependencies/IsaacLab is not initialized\n'
fi

print_section "Assets"
print_path_status "robot asset placeholder" "$REPO_ROOT/assets/robots"
print_path_status "scene asset placeholder" "$REPO_ROOT/assets/scenes"
find "$REPO_ROOT/assets" -maxdepth 3 -type f | sort

print_section "Local Isaac Installs"
if [ -f "$HOME/isaacsim/VERSION" ]; then
    printf 'local_isaacsim: '
    cat "$HOME/isaacsim/VERSION"
    printf '\n'
else
    printf '[missing] %s\n' "$HOME/isaacsim/VERSION"
fi

if [ -d "$HOME/IsaacLab/.git" ]; then
    printf 'local_isaaclab: '
    git -C "$HOME/IsaacLab" describe --tags --always
    printf 'local_isaaclab_branch: '
    git -C "$HOME/IsaacLab" branch --show-current
else
    printf '[missing] %s\n' "$HOME/IsaacLab"
fi

print_section "Compatibility Reminder"
cat <<'EOF'
LeIsaac docs state this matrix:
- Isaac Sim 4.5 -> IsaacLab v2.1.1
- Isaac Sim 5.0 -> IsaacLab v2.2.1
- Isaac Sim 5.1 -> IsaacLab v2.3.0

If you target Isaac Sim 4.5, check any code changes against IsaacLab v2.1.1 APIs before implementation.
EOF
