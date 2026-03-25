import threading
import time
from typing import Sequence

import numpy as np

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import JointState
except ImportError as exc:  # pragma: no cover - depends on ROS2 runtime
    rclpy = None
    Node = object
    qos_profile_sensor_data = None
    JointState = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class _FrankaJointStateNode(Node):
    def __init__(
        self,
        state_reader,
        node_name: str,
        joint_state_topic: str,
    ):
        super().__init__(node_name)
        self._state_reader = state_reader
        self.create_subscription(JointState, joint_state_topic, self._joint_state_callback, qos_profile_sensor_data)

    def _joint_state_callback(self, msg: JointState) -> None:
        self._state_reader.handle_joint_state(msg.name, msg.position)


class FrankaRos2StateReader:
    """ROS2 reader for real Franka joint and gripper states."""

    ARM_JOINT_NAME_CANDIDATES: tuple[tuple[str, ...], ...] = (
        (
            "panda_joint1",
            "panda_joint2",
            "panda_joint3",
            "panda_joint4",
            "panda_joint5",
            "panda_joint6",
            "panda_joint7",
        ),
        (
            "fr3_joint1",
            "fr3_joint2",
            "fr3_joint3",
            "fr3_joint4",
            "fr3_joint5",
            "fr3_joint6",
            "fr3_joint7",
        ),
    )
    FINGER_JOINT_NAME_CANDIDATES: tuple[tuple[str, ...], ...] = (
        (
            "panda_finger_joint1",
            "panda_finger_joint2",
        ),
        (
            "fr3_finger_joint1",
            "fr3_finger_joint2",
        ),
    )

    def __init__(
        self,
        ros_namespace: str = "",
        joint_state_topic: str | None = None,
        state_timeout: float = 1.0,
    ):
        if _IMPORT_ERROR is not None:  # pragma: no cover - depends on ROS2 runtime
            raise RuntimeError("ROS2 dependencies are unavailable. Install/activate a ROS2 environment first.") from _IMPORT_ERROR

        self._ros_namespace = ros_namespace.strip("/")
        self._joint_state_topic = self._resolve_topic(joint_state_topic or "joint_states")
        self._state_timeout = state_timeout
        self._lock = threading.Lock()
        self._latest_joint_state: np.ndarray | None = None
        self._latest_timestamp: float | None = None
        self._latest_names: tuple[str, ...] = ()
        self._last_gripper_state = np.array([0.04, 0.04], dtype=np.float32)
        self._matched_joint_family: str | None = None
        self._shutdown_event = threading.Event()

        self._owns_rclpy_context = False
        if not rclpy.ok():
            rclpy.init(args=None)
            self._owns_rclpy_context = True

        node_name = f"leisaac_franka_state_reader_{int(time.time() * 1000)}"
        self._node = _FrankaJointStateNode(self, node_name=node_name, joint_state_topic=self._joint_state_topic)
        self._spin_thread = threading.Thread(target=self._spin_loop, name=node_name, daemon=True)
        self._spin_thread.start()

    @property
    def joint_state_topic(self) -> str:
        return self._joint_state_topic

    def _resolve_topic(self, topic: str) -> str:
        if topic.startswith("/"):
            return topic
        if self._ros_namespace:
            return f"/{self._ros_namespace}/{topic}"
        return f"/{topic}"

    def _spin_loop(self) -> None:
        while not self._shutdown_event.is_set() and rclpy.ok():
            rclpy.spin_once(self._node, timeout_sec=0.1)

    def handle_joint_state(self, names: Sequence[str], positions: Sequence[float]) -> None:
        name_to_position = {name: position for name, position in zip(names, positions, strict=False)}
        arm_joint_names, finger_joint_names, matched_family = self._resolve_joint_name_family(name_to_position)
        if arm_joint_names is None or finger_joint_names is None:
            return

        arm_state = np.array([name_to_position[joint_name] for joint_name in arm_joint_names], dtype=np.float32)

        finger_positions = []
        for joint_name, default_position in zip(finger_joint_names, self._last_gripper_state, strict=False):
            finger_positions.append(name_to_position.get(joint_name, float(default_position)))
        gripper_state = np.array(finger_positions, dtype=np.float32)

        with self._lock:
            self._last_gripper_state = gripper_state
            self._latest_joint_state = np.concatenate([arm_state, gripper_state])
            self._latest_timestamp = time.monotonic()
            self._latest_names = tuple(names)
            self._matched_joint_family = matched_family

    def get_joint_state(self) -> np.ndarray | None:
        with self._lock:
            if self._latest_joint_state is None or self._latest_timestamp is None:
                return None
            if time.monotonic() - self._latest_timestamp > self._state_timeout:
                return None
            return self._latest_joint_state.copy()

    def get_debug_status(self) -> dict[str, object]:
        with self._lock:
            age = None if self._latest_timestamp is None else time.monotonic() - self._latest_timestamp
            return {
                "joint_state_topic": self._joint_state_topic,
                "has_state": self._latest_joint_state is not None,
                "state_age_sec": age,
                "latest_names": self._latest_names,
                "joint_family": self._matched_joint_family,
            }

    def close(self) -> None:
        self._shutdown_event.set()
        if hasattr(self, "_spin_thread") and self._spin_thread.is_alive():
            self._spin_thread.join(timeout=1.0)
        if hasattr(self, "_node"):
            self._node.destroy_node()
        if self._owns_rclpy_context and rclpy.ok():
            rclpy.shutdown()

    def _resolve_joint_name_family(self, name_to_position: dict[str, float]) -> tuple[tuple[str, ...] | None, tuple[str, ...] | None, str | None]:
        for family_name, arm_joint_names, finger_joint_names in (
            ("panda", self.ARM_JOINT_NAME_CANDIDATES[0], self.FINGER_JOINT_NAME_CANDIDATES[0]),
            ("fr3", self.ARM_JOINT_NAME_CANDIDATES[1], self.FINGER_JOINT_NAME_CANDIDATES[1]),
        ):
            if all(joint_name in name_to_position for joint_name in arm_joint_names):
                return arm_joint_names, finger_joint_names, family_name
        return None, None, None
