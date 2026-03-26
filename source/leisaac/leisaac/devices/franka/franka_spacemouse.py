from isaaclab.devices import Se3SpaceMouse

from ..device_base import Device


class FrankaSpaceMouse(Device):
    """SpaceMouse teleop wrapper for Franka using Isaac Lab's SE(3) spacemouse device."""

    def __init__(self, env, sensitivity: float = 1.0):
        super().__init__(env, "franka-spacemouse")
        self._started = True
        self._se3_device = Se3SpaceMouse(
            pos_sensitivity=0.05 * sensitivity,
            rot_sensitivity=0.1 * sensitivity,
        )

    def __del__(self):
        if hasattr(self, "_se3_device"):
            del self._se3_device
        super().__del__()

    def _add_device_control_description(self):
        self._display_controls_table.add_row(["SpaceMouse move", "translate end-effector"])
        self._display_controls_table.add_row(["SpaceMouse twist", "rotate end-effector"])
        self._display_controls_table.add_row(["Left button", "toggle gripper"])
        self._display_controls_table.add_row(["Right button", "reset local spacemouse command"])

    def get_device_state(self):
        return self._se3_device.advance()

    def reset(self):
        self._started = True
        self._reset_state = False
        self._se3_device.reset()

    def _split_command(self):
        command = self.get_device_state()
        if isinstance(command, (tuple, list)):
            delta_pose, gripper_command = command
            return delta_pose, bool(gripper_command)
        delta_pose = command[:6]
        gripper_command = bool(command[6] < 0)
        return delta_pose, gripper_command

    def input2action(self):
        reset = self._reset_state
        action = {
            "reset": reset,
            "started": self.started,
            self.device_type: True,
        }
        if reset:
            self._reset_state = False
            return action
        delta_pose, gripper_command = self._split_command()
        action["delta_pose"] = delta_pose
        action["gripper_command"] = gripper_command
        return action
