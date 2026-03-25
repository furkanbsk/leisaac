# Franka Dataset Pipeline Notes

This note captures the current dataset handling rules for the Franka port.

## Supported Task And Device Pair

The first supported Franka task pair is:

- task: `LeIsaac-Franka-LiftCube-v0`
- teleop devices:
  - `franka-keyboard`
  - `franka-spacemouse`

## Recording

Use the teleoperation script with one of the Franka teleop devices.

Examples:

```bash
python scripts/environments/teleoperation/teleop_se3_agent.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --teleop_device franka-keyboard \
  --num_envs 1 \
  --record \
  --dataset_file ./datasets/franka_liftcube.hdf5
```

```bash
python scripts/environments/teleoperation/teleop_se3_agent.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --teleop_device franka-spacemouse \
  --num_envs 1 \
  --record \
  --dataset_file ./datasets/franka_liftcube.hdf5
```

## Replay

For Franka teleop datasets, use:

```bash
python scripts/environments/teleoperation/replay.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --task_type franka-keyboard \
  --dataset_file ./datasets/franka_liftcube.hdf5 \
  --replay_mode action
```

State replay is intentionally blocked for Franka teleop datasets.

Reason:

- Franka teleop actions are stored as differential IK end-effector deltas plus a binary gripper command
- the recorded articulation state is joint-space
- these spaces are not interchangeable

## LeRobot Export

The Franka teleop pipeline currently exports:

- `observation.state`: joint-space state using the Franka joint profile
- `action`: 7-dimensional teleop action

Since the Franka teleop action dimension does not match the Franka joint-state dimension, dataset export uses the
non-aligned action path.

This is expected behavior.
