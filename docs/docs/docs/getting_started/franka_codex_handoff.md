# Franka Codex Handoff

Bu dosya, remote `lira` makinesinde yeni bir Codex oturumu açıldığında projenin hangi noktada olduğunu hızlıca anlatmak için tutulur.

## Amaç

Ana hedef:

- Gerçek Franka robotunu `leader` olarak kullanmak
- Isaac Sim içindeki Franka'yı `follower` olarak sürmek
- Simülasyonda dataset toplamak

Bu amaç için `leisaac` içinde Franka task'leri, `franka-leader` device hattı ve dataset record/replay akışı hazırlandı.

## Repo ve Branch

- Repo: `~/furkan_workspace/leisaac`
- Branch: `franka-phase0-baseline`

## Doğrulanan Şeyler

### Sim / Isaac tarafı

- `LeIsaac-Franka-LiftCube-v0` task'i çalışıyor
- `LeIsaac-Franka-BowlCubeZone-v0` custom task'i çalışıyor
- Franka keyboard teleop path'i düzeltildi
- `record -> replay(action)` hattı doğrulandı
- `franka-leader` device eklendi

### Ağ tarafı

Remote makinede iki ağ aynı anda çalışıyor:

- Wi-Fi:
  - interface: `wlp3s0`
  - IP: `10.205.214.215/23`
- Franka Ethernet:
  - interface: `enp4s0`
  - IP: `172.16.0.1/24`
- Robot:
  - IP: `172.16.0.2`

Doğrulanan test:

```bash
ping -I enp4s0 -c 2 172.16.0.2
```

## En Son Denenen Şey

Gerçek robot için `franka_ros2` bringup çalıştırıldı:

```bash
source /opt/ros/humble/setup.bash
source ~/franka_ros2_ws/install/setup.bash

ros2 launch franka_bringup franka.launch.py \
  robot_type:=fr3 \
  robot_ip:=172.16.0.2 \
  load_gripper:=false \
  use_fake_hardware:=false \
  joint_state_rate:=30
```

## Mevcut Blocker

Bringup şu hata ile duruyor:

```text
libfranka: Connection to FCI refused. Please install FCI feature or enable FCI mode in Desk.
```

Bu şu anlama geliyor:

- ağ erişimi tamam
- robot cevap veriyor
- ama Desk tarafında FCI açık değil ya da FCI feature kurulu değil

## Desk Erişimi

Robot Desk erişilebilir:

- `https://172.16.0.2/desk/`

Remote makinede bir browser açıp ya da başka bir cihazdan aynı ağa bağlı şekilde Desk'e girilebilir.

## Desk Tarafında Yapılacaklar

1. Robotu normal şekilde hazır duruma getir
2. Gerekirse brake/activation adımlarını tamamla
3. Desk içinde `Activate FCI` aç
4. Gerekirse FCI feature'ın kurulu olduğunu doğrula

## FCI Açıldıktan Sonra İlk Komutlar

### 1. Bringup

```bash
source /opt/ros/humble/setup.bash
source ~/franka_ros2_ws/install/setup.bash

ros2 launch franka_bringup franka.launch.py \
  robot_type:=fr3 \
  robot_ip:=172.16.0.2 \
  load_gripper:=false \
  use_fake_hardware:=false \
  joint_state_rate:=30
```

### 2. Joint states kontrolü

Yeni terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/franka_ros2_ws/install/setup.bash

ros2 topic list | grep joint_states
ros2 topic echo /joint_states --once
```

Beklenti:

- `/joint_states`
- `fr3_joint1..7`
- gerekirse finger joint'ler

### 3. Real -> Sim smoke

Yeni terminal:

```bash
source /home/lira/miniconda3/etc/profile.d/conda.sh
conda activate env_isaacsim
source /home/lira/isaacsim/setup_conda_env.sh
cd ~/furkan_workspace/leisaac

/home/lira/IsaacLab/isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task LeIsaac-Franka-LiftCube-v0 \
  --teleop_device franka-leader \
  --num_envs 1 \
  --enable_cameras
```

Not:

- Eğer `home` path'leri farklıysa bu komutları ona göre düzelt
- Remote makinede IsaacLab ve conda env zaten kuruluydu; daha önce fake smoke geçti

## BowlCubeZone Sahnesi

Custom sahne:

- task: `LeIsaac-Franka-BowlCubeZone-v0`
- marker var
- bowl yerine `Lightwheel Kitchen_Disk002` plate asset kullanılıyor

İlgili config:

- [bowl_cube_zone_env_cfg.py](/home/nvidia/leisaac/source/leisaac/leisaac/tasks/bowl_cube_zone/bowl_cube_zone_env_cfg.py)

## İlgili Ana Notlar

- [franka_setup.md](/home/nvidia/leisaac/docs/docs/docs/getting_started/franka_setup.md)
- [franka_real_to_sim_roadmap.md](/home/nvidia/leisaac/docs/docs/docs/getting_started/franka_real_to_sim_roadmap.md)

## Yeni Codex Oturumuna Kısa Talimat

Bu repo remote `lira` makinesinde açıldığında önce şunu yap:

1. `franka_setup.md` ve bu handoff dosyasını oku
2. `ping -I enp4s0 -c 2 172.16.0.2` ile robot erişimini doğrula
3. FCI açıksa `franka_bringup` başlat
4. `/joint_states` geliyorsa `franka-leader` ile real-to-sim smoke yap
5. Sonra dataset recording aşamasına geç
