# Franka Real-to-Sim Smoke

Bu doküman aynı makinede çalışan ilk `real leader -> sim follower` smoke akışını tanımlar.

## Hazır Durum

- `franka_ros2` workspace varsayılanı: `$HOME/franka_ros2_ws`
- Build edilen temel paketler:
  - `franka_bringup`
  - `franka_hardware`
  - `franka_gripper`
  - `franka_robot_state_broadcaster`
- LeIsaac tarafında `franka-leader` device eklendi.

## Taşınabilir Dış Bağımlılık Değişkenleri

Helper scriptler artık şu env var'ları kullanır:

- `CONDA_SH`
- `CONDA_ENV_NAME`
- `ISAACSIM_ROOT`
- `ISAACLAB_ROOT`
- `ROS_DISTRO`
- `ROS_SETUP`
- `ROS_WS`

Yeni makinede hızlı kontrol:

```bash
bash scripts/tutorials/check_franka_external_stack.sh
```

## Kritik Not

`franka_ros2` fake/real bringup bu makinada `panda_*` değil, `fr3_*` joint isimleri yayınlıyor:

- `fr3_joint1..7`
- `fr3_finger_joint1`
- `fr3_finger_joint2`

Bu yüzden `FrankaLeader` reader artık hem `panda_*` hem `fr3_*` ailelerini kabul eder ve sim Franka action formatına map eder.

## Repeatable Fake-Hardware Smoke

Bu komut fake Franka bringup başlatır, `/joint_states` doğrular ve LeIsaac içinde headless follower smoke çalıştırır:

```bash
bash scripts/tutorials/check_franka_real_to_sim_fake_smoke.sh
```

Başarı çıktısı:

```text
leader_smoke_ok {...}
```

Bu şu zinciri doğrular:

- `franka_bringup` fake hardware launch
- `/joint_states` yayını
- `FrankaLeader` ROS2 subscriber
- `LeIsaac-Franka-LiftCube-v0`
- sim Franka follower action step

## Gerçek Robot İçin Operasyon Sırası

1. ROS 2 ortamını aç:

```bash
source "${ROS_SETUP:-/opt/ros/humble/setup.bash}"
source "${ROS_WS:-$HOME/franka_ros2_ws}/install/setup.bash"
```

2. Gerçek Franka bringup başlat:

```bash
ros2 launch franka_bringup franka.launch.py \
  robot_type:=fr3 \
  robot_ip:=<robot_ip> \
  load_gripper:=true \
  joint_state_rate:=30
```

3. Topic’i doğrula:

```bash
ros2 topic list | grep joint_states
timeout 5 ros2 topic echo /joint_states --once
```

4. Isaac/LeIsaac tarafını aç:

```bash
source "${CONDA_SH:-$HOME/miniconda3/etc/profile.d/conda.sh}"
conda activate "${CONDA_ENV_NAME:-env_isaacsim}"
source "${ISAACSIM_ROOT:-$HOME/isaacsim}/setup_conda_env.sh"

cd /path/to/leisaac
"${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh" -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --teleop_device franka-leader \
  --num_envs 1 \
  --enable_cameras \
  --joint_state_topic /joint_states
```

## Taşıma Notu

Repo tek başına yeterli değildir. Yeni makinede ayrıca şunlar hazır olmalı:

- Isaac Sim
- IsaacLab
- `env_isaacsim` veya eşdeğer conda env
- `franka_ros2` workspace
- Isaac Sim AppLauncher uyumluluğu için gerekli `isaacsim` shim durumu

Hızlı dış-bağımlılık kontrolü:

```bash
bash scripts/tutorials/check_franka_external_stack.sh
```

## Motion Authority

Bu aşamada:

- gerçek Franka yalnız `leader`
- LeIsaac gerçek robota command göndermez
- sim Franka yalnız follower olarak hareket eder
- gerçek robottaki guiding / hand-guiding modu operatör tarafından yönetilir
