# Franka Port Phase 0 Baseline

This note captures the initial repository and workstation state before starting the Franka port.

## Goal

Phase 0 exists to freeze the working baseline before making robot-specific changes. The intent is:

- initialize all required source dependencies
- verify which Isaac versions are actually present on the workstation
- identify blocking gaps such as missing assets
- record compatibility constraints for Isaac Sim 4.5 work

## Current Baseline

On this workstation, the following state was confirmed:

- local Isaac Sim binary: `4.5.0-rc.36+release.19112.f59b3005.gl`
- local standalone IsaacLab checkout: `v2.1.1-4-g19b24c780e` on `main`
- `leisaac` repository branch for this work: `franka-phase0-baseline`
- `leisaac` submodule `dependencies/IsaacLab` initialized at `v2.3.0`
- `assets/robots` and `assets/scenes` only contain `.gitkeep` placeholders

## Important Constraint

LeIsaac's installation guide states the following compatibility table:

- Isaac Sim 4.5 -> IsaacLab `v2.1.1`
- Isaac Sim 5.0 -> IsaacLab `v2.2.1`
- Isaac Sim 5.1 -> IsaacLab `v2.3.0`

That means Franka implementation for the current workstation must be checked against IsaacLab `v2.1.1` behavior, even if the `leisaac` submodule is presently pinned to `v2.3.0`.

Reference: [installation.md](/home/nvidia/leisaac/docs/docs/docs/getting_started/installation.md#L66)

## Phase 0 Checklist

- repo branch created for Franka porting work
- `dependencies/IsaacLab` submodule initialized
- local Isaac versions recorded
- asset gaps identified
- repeatable audit command added

## Repeatable Audit

Run the following from the repo root:

```bash
bash scripts/tutorials/check_franka_phase0.sh
```

This prints:

- repo branch and working tree state
- submodule status
- asset presence
- local Isaac Sim version
- local IsaacLab version
- the compatibility reminder for Isaac Sim 4.5 work

## Known Blockers Before Phase 1

- Franka-specific USD / articulation config is not present in `leisaac`
- required scene assets are not downloaded into `assets/`
- `leisaac` still contains SO101-specific assumptions in task templates and action processing
- the repo-level IsaacLab submodule is newer than the workstation's Isaac Sim 4.5 target stack

## Exit Criteria For Phase 0

Phase 0 is complete when:

- the workspace state is reproducible
- the dependency and asset gaps are explicit
- implementation work can start without ambiguity about versions
