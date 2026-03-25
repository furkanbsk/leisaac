# LeIsaac 🚀

https://github.com/user-attachments/assets/763acf27-d9a9-4163-8651-3ba0a6a185d7

This repository provides teleoperation functionality in [IsaacLab](https://isaac-sim.github.io/IsaacLab/main/index.html) using the SO101Leader ([LeRobot](https://github.com/huggingface/lerobot)), including data collection, data conversion, and subsequent policy training.

- 🤖 We use SO101Follower as the robot (and other related robot) in IsaacLab and provide relevant teleoperation method.
- 🔄 We offer scripts to convert data from HDF5 format to the LeRobot Dataset.
- 🧠 We utilize simulation-collected data to fine-tune [GR00T N1.5](https://github.com/NVIDIA/Isaac-GR00T) and deploy it on real hardware. And more policies will be supported.

> [!TIP]
> ***Welcome to the Lightwheel open-source community!***
>
> Join us, contribute, and help shape the future of AI and robotics. For questions or collaboration, contact [Zeyu](mailto:zeyu.hu@lightwheel.ai) or [Yinghao](mailto:yinghao.shuai@lightwheel.ai).

## Getting Started 📚

Please refer to our [documentation](https://lightwheelai.github.io/leisaac/) to learn how to use this repository. Follow these links to learn more about:

- [Installation and Setup](https://lightwheelai.github.io/leisaac/docs/getting_started/installation)
- [Extra Features](https://lightwheelai.github.io/leisaac/docs/features)
- [Policy Inference](https://lightwheelai.github.io/leisaac/docs/getting_started/policy_support)
- [Available Robots](https://lightwheelai.github.io/leisaac/resources/available_robots), [Environments](https://lightwheelai.github.io/leisaac/resources/available_env) and [Policy](https://lightwheelai.github.io/leisaac/resources/available_policy)

> [!TIP]
>
> For more features and updates, please refer to the [News](https://lightwheelai.github.io/leisaac/#news) section on our website!

## Franka Real-to-Sim Quickstart

This fork also contains a Franka `real leader -> sim follower -> dataset` path built on top of `franka_ros2`.

Validated stack:

- Isaac Sim `4.5`
- IsaacLab `19b24c780ea` (`v2.1.1-4`)
- ROS 2 `Humble`
- `franka_ros2`

Important notes:

- The current Franka path is for `real Franka state -> simulated Franka follower`.
- LeIsaac does not command the real Franka in this mode.
- The real robot must already be in a safe hand-guiding / guiding workflow managed on the robot side.
- On some systems, Franka ROS publishes `fr3_*` joint names instead of `panda_*`; this fork handles both.

Environment check:

```bash
bash scripts/tutorials/check_franka_external_stack.sh
```

Fake-hardware smoke:

```bash
bash scripts/tutorials/check_franka_real_to_sim_fake_smoke.sh
bash scripts/tutorials/check_franka_real_to_sim_record_replay_fake_smoke.sh
```

Live robot bring-up:

```bash
source /opt/ros/humble/setup.bash
source "$HOME/franka_ros2_ws/install/setup.bash"

ros2 launch franka_bringup franka.launch.py \
  robot_type:=fr3 \
  robot_ip:=<robot_ip> \
  load_gripper:=true \
  joint_state_rate:=30
```

Check live state:

```bash
ros2 topic list | grep joint_states
timeout 5 ros2 topic echo /joint_states --once
```

Run the follower in Isaac Sim:

```bash
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate env_isaacsim

cd /path/to/leisaac
"$HOME/IsaacLab/isaaclab.sh" -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --teleop_device franka-leader \
  --num_envs 1 \
  --enable_cameras \
  --joint_state_topic /joint_states
```

Record a dataset:

```bash
"$HOME/IsaacLab/isaaclab.sh" -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --teleop_device franka-leader \
  --num_envs 1 \
  --enable_cameras \
  --joint_state_topic /joint_states \
  --record \
  --dataset_file ./datasets/franka_leader_live.hdf5
```

Replay the dataset:

```bash
"$HOME/IsaacLab/isaaclab.sh" -p scripts/environments/teleoperation/replay.py \
  --headless \
  --enable_cameras \
  --task LeIsaac-Franka-LiftCube-v0 \
  --task_type franka-leader \
  --dataset_file ./datasets/franka_leader_live.hdf5 \
  --replay_mode action
```

See also:

- [Franka real-to-sim smoke doc](./docs/docs/docs/getting_started/franka_real_to_sim_smoke.md)
- [Franka roadmap](./docs/docs/docs/getting_started/franka_real_to_sim_roadmap.md)

## Citation 📝

If you use leisaac, please cite it as follows.

```txt
@software{Lightwheel_and_LeIsaac_Project_Developers_LeIsaac_2025,
author = {{Lightwheel} and {LeIsaac Project Developers}},
license = {Apache-2.0},
month = dec,
title = {{LeIsaac}},
url = {https://github.com/LightwheelAI/leisaac},
version = {0.3.0},
year = {2025}
}
```

## Acknowledgements 🙏

We gratefully acknowledge [IsaacLab](https://github.com/isaac-sim/IsaacLab) and [LeRobot](https://github.com/huggingface/lerobot) for their excellent work, from which we have borrowed some code.

## Join Our Team! 💼

We're always looking for talented individuals passionate about AI and robotics! If you're interested in:

- 🤖 **Robotics Engineering**: Working with cutting-edge robotic systems and teleoperation
- 🧠 **AI/ML Research**: Developing next-generation AI models for robotics
- 💻 **Software Engineering**: Building robust, scalable robotics software
- 🔬 **Research & Development**: Pushing the boundaries of what's possible in robotics

**Join us at Lightwheel AI!** We offer:
- Competitive compensation and benefits
- Work with state-of-the-art robotics technology
- Collaborative, innovative environment
- Opportunity to shape the future of AI-powered robotics

**[Apply Now →](https://lightwheel.ai/career)** | **[Contact Now →](mailto:zeyu.hu@lightwheel.ai)** | **[Learn More About Us →](https://lightwheel.ai)**

---

**Let's build the future of robotics together! 🤝**

---
