from isaaclab.devices import Se3Keyboard

from ..device_base import Device


class FrankaKeyboard(Device):
    """Keyboard teleop wrapper for Franka using Isaac Lab's SE(3) keyboard device."""

    def __init__(self, env, sensitivity: float = 1.0):
        super().__init__(env, "franka-keyboard")
        self._started = True
        self._se3_device = Se3Keyboard(
            pos_sensitivity=0.05 * sensitivity,
            rot_sensitivity=0.05 * sensitivity,
        )

    def __del__(self):
        if hasattr(self, "_se3_device"):
            del self._se3_device
        super().__del__()

    def _add_device_control_description(self):
        self._display_controls_table.add_row(["W/S", "move end-effector along x"])
        self._display_controls_table.add_row(["A/D", "move end-effector along y"])
        self._display_controls_table.add_row(["Q/E", "move end-effector along z"])
        self._display_controls_table.add_row(["Z/X", "rotate around x"])
        self._display_controls_table.add_row(["T/G", "rotate around y"])
        self._display_controls_table.add_row(["C/V", "rotate around z"])
        self._display_controls_table.add_row(["K", "toggle gripper"])

    def get_device_state(self):
        return self._se3_device.advance()

    def reset(self):
        self._started = True
        self._reset_state = False
        self._se3_device.reset()

    def _split_command(self):
        command = self.get_device_state()
        # Isaac Lab 2.1.x returns a single 7D tensor: [dx, dy, dz, rx, ry, rz, gripper].
        # Older wrappers expected a tuple of (delta_pose, gripper_command), so support both.
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
