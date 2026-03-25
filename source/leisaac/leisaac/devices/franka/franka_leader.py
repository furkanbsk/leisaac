from __future__ import annotations

from ..device_base import Device
from .ros2_state_reader import FrankaRos2StateReader


class FrankaLeader(Device):
    """Real Franka leader adapter that mirrors ROS2 joint state into sim Franka actions."""

    def __init__(
        self,
        env,
        ros_namespace: str = "",
        joint_state_topic: str | None = None,
        state_timeout: float = 1.0,
    ):
        self._joint_state_topic_hint = self._resolve_topic_hint(ros_namespace, joint_state_topic)
        super().__init__(env, "franka-leader")
        self._state_reader = FrankaRos2StateReader(
            ros_namespace=ros_namespace,
            joint_state_topic=joint_state_topic,
            state_timeout=state_timeout,
        )

    def __del__(self):
        if hasattr(self, "_state_reader"):
            self._state_reader.close()
        super().__del__()

    def _add_device_control_description(self):
        topic = getattr(self, "_joint_state_topic_hint", "/joint_states")
        self._display_controls_table.add_row(
            ["Leader", "move the real Franka by hand after enabling the robot's guiding/hand-guiding mode"]
        )
        self._display_controls_table.add_row(
            ["ROS2", f"reads latest joint state from {topic} and mirrors it into sim"]
        )
        self._display_controls_table.add_row(
            ["[TIPS]", "If sim does not move, verify ROS2 joint_states are publishing and press B after the app gains focus"]
        )

    def get_device_state(self):
        return self._state_reader.get_joint_state()

    def reset(self):
        pass

    def input2action(self):
        reset = self._reset_state
        if reset:
            self._reset_state = False
            return {
                "reset": reset,
                "started": False,
                self.device_type: True,
            }

        joint_state = self.get_device_state()
        if joint_state is None:
            return None

        # Real leader devices should not depend on keyboard focus for startup.
        self._started = True
        return {
            "reset": False,
            "started": True,
            self.device_type: True,
            "joint_state": joint_state,
        }

    @staticmethod
    def _resolve_topic_hint(ros_namespace: str, joint_state_topic: str | None) -> str:
        topic = joint_state_topic or "joint_states"
        if topic.startswith("/"):
            return topic
        ros_namespace = ros_namespace.strip("/")
        if ros_namespace:
            return f"/{ros_namespace}/{topic}"
        return f"/{topic}"
