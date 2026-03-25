# Franka Phase 6 Smoke Test

Phase 6 focuses on runtime validation of the first Franka task path:

- task: `LeIsaac-Franka-LiftCube-v0`
- teleop: `franka-keyboard` or `franka-spacemouse`
- record -> replay(action) -> convert

## Workstation Status

The initial blockers on this workstation have been reduced:

1. The required scene asset is now installed:
   - `assets/scenes/table_with_cube/scene.usd`
2. The smoke path must run from `env_isaacsim` with Isaac Sim's environment sourced:
   - `conda activate env_isaacsim`
   - `source ${ISAACSIM_ROOT:-$HOME/isaacsim}/setup_conda_env.sh`
3. The local Isaac Sim shim at `${ISAACSIM_ROOT:-$HOME/isaacsim}/__init__.py` needed a compatibility fix so
   `from isaacsim import SimulationApp` works with IsaacLab's `AppLauncher`.

## Repeatable Smoke Check

Run:

```bash
bash scripts/tutorials/check_franka_phase6_smoke.sh
```

This check validates:

- whether the `table_with_cube` scene exists
- whether Isaac Kit can launch headless
- whether `LeIsaac-Franka-LiftCube-v0` can be created, reset, and stepped once

## Expected Next Step

Once the smoke check passes, the first interactive target should be:

```bash
source "${CONDA_SH:-$HOME/miniconda3/etc/profile.d/conda.sh}"
conda activate "${CONDA_ENV_NAME:-env_isaacsim}"
source "${ISAACSIM_ROOT:-$HOME/isaacsim}/setup_conda_env.sh"

"${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh" -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --teleop_device franka-keyboard \
  --num_envs 1
```

Then:

```bash
"${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh" -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --teleop_device franka-keyboard \
  --num_envs 1 \
  --record \
  --dataset_file ./datasets/franka_liftcube.hdf5
```

And replay:

```bash
"${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh" -p scripts/environments/teleoperation/replay.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --task_type franka-keyboard \
  --dataset_file ./datasets/franka_liftcube.hdf5 \
  --replay_mode action
```
