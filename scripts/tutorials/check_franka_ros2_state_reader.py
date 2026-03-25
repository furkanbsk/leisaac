"""Smoke test for Franka ROS2 joint-state reader using a local JointState publisher."""

from __future__ import annotations

import time
from pathlib import Path
import sys
import importlib.util

REPO_ROOT = Path(__file__).resolve().parents[2]
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

STATE_READER_PATH = REPO_ROOT / "source" / "leisaac" / "leisaac" / "devices" / "franka" / "ros2_state_reader.py"
spec = importlib.util.spec_from_file_location("franka_ros2_state_reader", STATE_READER_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
FrankaRos2StateReader = module.FrankaRos2StateReader


class JointStatePublisher(Node):
    def __init__(self, topic: str):
        super().__init__("franka_state_reader_smoke_publisher")
        self._publisher = self.create_publisher(JointState, topic, 10)

    def publish_sample(self) -> None:
        msg = JointState()
        msg.name = [
            "panda_joint1",
            "panda_joint2",
            "panda_joint3",
            "panda_joint4",
            "panda_joint5",
            "panda_joint6",
            "panda_joint7",
            "panda_finger_joint1",
            "panda_finger_joint2",
        ]
        msg.position = [0.1, -0.2, 0.3, -1.2, 0.5, 1.0, 0.7, 0.03, 0.03]
        self._publisher.publish(msg)


def main() -> None:
    topic = "/joint_states"
    if not rclpy.ok():
        rclpy.init(args=None)

    publisher = JointStatePublisher(topic)
    reader = FrankaRos2StateReader(joint_state_topic=topic, state_timeout=1.0)
    try:
        deadline = time.time() + 2.0
        while time.time() < deadline:
            publisher.publish_sample()
            time.sleep(0.1)
            state = reader.get_joint_state()
            if state is not None:
                print("reader_ok", state.tolist())
                return
        raise RuntimeError("FrankaRos2StateReader did not receive any sample within the timeout.")
    finally:
        reader.close()
        publisher.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
