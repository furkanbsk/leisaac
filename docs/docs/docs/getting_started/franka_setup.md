# Franka Setup

Bu not, `lira` remote makinesinde gerçek Franka robotuna erişim için gereken ağ ve çalışma durumunu toplar.

## Amaç

- Remote PC Wi-Fi üzerinden erişilebilir kalsın
- Aynı anda Ethernet üzerinden Franka'ya bağlı olsun
- `franka_ros2` ve `leisaac` bu makinede kullanılabilsin

## Doğrulanan Makine

- Host: `lira-B660M-DS3H-AX-DDR4`
- Repo: `~/furkan_workspace/leisaac`
- Branch: `franka-phase0-baseline`
- Wi-Fi arayüzü: `wlp3s0`
- Franka Ethernet arayüzü: `enp4s0`

## Doğrulanan Ağ Durumu

- Wi-Fi bağlantısı aktif:
  - SSID: `EA-05`
  - IP: `10.205.214.215/23`
- Franka Ethernet bağlantısı aktif:
  - Interface: `enp4s0`
  - Static IP: `172.16.0.1/24`
  - `never-default`: `yes`
- Franka robot IP:
  - `172.16.0.2`

## Doğrulanan Testler

- `wlp3s0` üzerinden remote SSH çalışıyor
- `enp4s0` üzerinden Franka `172.16.0.2` ping cevaplıyor
- Wi-Fi default route olarak kalıyor
- Franka subnet route'u yalnız `enp4s0` üzerinden gidiyor

Örnek doğrulama:

```bash
ip -br addr
ip route
ping -I enp4s0 -c 2 172.16.0.2
```

Beklenen çıktı özeti:

- `wlp3s0` üzerinde `10.205.214.215/23`
- `enp4s0` üzerinde `172.16.0.1/24`
- `ping -I enp4s0 172.16.0.2` başarılı

## Kalıcı NetworkManager Ayarı

`Wired connection 1` Franka için şu profile ayarlandı:

```bash
nmcli connection modify 'Wired connection 1' \
  ipv4.method manual \
  ipv4.addresses 172.16.0.1/24 \
  ipv4.gateway '' \
  ipv4.dns '' \
  ipv4.never-default yes \
  ipv6.method ignore
```

Beklenen aktif durum:

```bash
nmcli connection show 'Wired connection 1'
```

Önemli alanlar:

- `ipv4.method: manual`
- `ipv4.addresses: 172.16.0.1/24`
- `ipv4.never-default: yes`
- `ipv6.method: ignore`
- `GENERAL.STATE: activated`

## Bağlantı Yeniden Kurma

Remote makine reboot sonrası Wi-Fi geldikten sonra aşağıyı kontrol et:

```bash
nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device
ip -br addr
ip route
ping -I enp4s0 -c 2 172.16.0.2
```

Eğer `enp4s0` IP almamışsa:

```bash
echo lira | sudo -S nmcli connection up 'Wired connection 1' ifname enp4s0
```

Eğer buna rağmen düzelmezse geçici kurtarma:

```bash
echo lira | sudo -S ip addr flush dev enp4s0
echo lira | sudo -S ip addr add 172.16.0.1/24 dev enp4s0
ping -I enp4s0 -c 2 172.16.0.2
```

## SSH Erişimi

Ethernet Franka'ya takılıyken remote PC'ye Wi-Fi IP üzerinden bağlan:

```bash
ssh lira@10.205.214.215
```

## Sonraki Adım

Gerçek robot erişimi doğrulandıktan sonra sıradaki iş:

1. `franka_ros2` bringup
2. `/joint_states` doğrulama
3. `franka-leader` ile `real -> sim` smoke
4. dataset record/replay

Remote'da yeni bir Codex oturumu açılacaksa önce şu dosyayı oku:

- [franka_codex_handoff.md](/home/nvidia/leisaac/docs/docs/docs/getting_started/franka_codex_handoff.md)

## Mevcut Blocker

Network katmanı çalışıyor ancak `franka_ros2` gerçek donanım bringup şu hata ile duruyor:

```text
libfranka: Connection to FCI refused. Please install FCI feature or enable FCI mode in Desk.
```

Bu hata ilk bakışta yalnızca FCI kapalı gibi görünür, ama artık elimizde ek bulgular var:

- `Installed Features` içinde FCI görünüyor
- Robot Desk erişilebilir
- `172.16.0.2:1337` açık
- FR3 resmi dokümanında `Activate FCI` sonrası sidebar'ın yeşil olması beklenen davranış
- Doküman robot üzerinde ayrıca bir FCI tuşuna basılması gerektiğini söylemiyor

Doğrulanan durum:

- Robot web arayüzü erişilebilir:
  - `https://172.16.0.2/desk/`
- Ağ erişimi tamam:
  - `ping -I enp4s0 172.16.0.2` başarılı
- FCI tarafı reddediliyor:
  - `ros2 launch franka_bringup franka.launch.py ...` başarısız

## Kök Neden ve Çözüm

İki ayrı problem vardı:

1. `libfranka/franka_ros2` sürümü fazla yeniydi
2. Remote makinede `ufw` robotun host'a yolladığı UDP akışını düşürüyordu

Doğrulanan uyumlu stack:

- Robot system version:
  - `5.4.0`
- Uyumlu `libfranka`:
  - `0.12.1`
- Uyumlu `franka_ros2`:
  - `v0.1.7`

Resmi kaynaklar:

- `libfranka 0.12.1` -> `Requires Franka Research 3 system version >= 5.2.0`
- `libfranka 0.13.3` -> `Requires Franka Research 3 system version >= 5.5.0`
- `franka_ros2 v0.1.8` -> `Requires libfranka >= 0.13.0`

Yani `5.4.0` için güvenli kombinasyon:

- `libfranka 0.12.1`
- `franka_ros2 v0.1.7`

Eski şüphe notu:

- Remote PC'de kurulu `franka_hardware`:
  - `2.3.0`
- Remote PC'de kurulu `ros-humble-libfranka`:
  - `0.20.4`
- Robot Desk HTML yanıtı:
  - `Last-Modified: Thu, 21 Sep 2023 14:48:16 GMT`
- Güncel `libfranka-common` robot komut protokolü:
  - `kVersion = 10`

Bu tablo, robot kontrol ünitesinin daha eski bir system image / FCI protokolüyle
çalışıp 2026 tarihli `libfranka 0.20.4` istemcisini reddettiğini gösterdi.

## UFW Gereksinimi

Remote makinede `ufw` aktif ve default incoming policy `deny`.

FCI handshake sonrası robot, host'a yeni UDP paketleri açıyor. Bunlar firewall tarafından
düşüyordu. Bu yüzden:

- `tcpdump` UDP paketlerini görüyordu
- ama `libfranka` `UDP receive: Timeout` veriyordu

Kalıcı çözüm:

```bash
echo lira | sudo -S ufw allow in on enp4s0 from 172.16.0.2 comment 'Franka FCI UDP'
```

## Desk Tarafında Yapılması Gerekenler

Desk üzerinde:

1. Brakeleri çöz
2. Robotu execution-ready duruma getir
3. Menüden `Activate FCI` seç
4. FR3 için çıkan confirm adımını tamamla
5. Gerekirse çıkan onay penceresini açık bırak

Ek kontrol:

- `Settings -> System -> Installed Features` altında FCI feature kurulu olmalı

Not:

- FR3 dokümanında `Activate FCI` sonrası sidebar'ın yeşil olması normal davranış olarak gösteriliyor
- Robot üzerinde ayrıca basılması gereken özel bir FCI tuşu dokümante edilmiyor

## FCI Açıldıktan Sonra Doğrulama

Remote PC üzerinde:

```bash
/home/nvidia/leisaac/scripts/tutorials/run_franka_54_bringup.sh
```

Ayrı terminalde:

```bash
source /opt/ros/humble/setup.bash
source ~/franka_ros2_ws/install/setup.bash

ros2 topic list | grep joint_states
ros2 topic echo /joint_states --once
```

Beklenen topicler:

- `/joint_states`
- `/franka/joint_states`
- `/dynamic_joint_states`

Beklenen joint isimleri:

- `panda_joint1..7`

## Kurulum Scripti

Remote makinede uyumlu stack'i tekrar kurmak için:

```bash
cd ~/furkan_workspace/leisaac
chmod +x scripts/tutorials/setup_franka_54_compat_ws.sh
echo lira | sudo -S scripts/tutorials/setup_franka_54_compat_ws.sh
```

Script:

- `franka_ros2 v0.1.7` çeker
- `libfranka 0.12.1` çeker
- `~/franka_compat_prefix` altına kurar
- `franka_semantic_components` için Humble uyum patch'i uygular
- `~/franka_ros2_54_ws` overlay workspace'ini derler
- `ufw` kuralını ekler

## Doğrulanan Sonuç

Bu kombinasyonla şu aşamalar geçti:

- gerçek robot bringup
- `/joint_states` yayını
- `franka-leader` ile headless `real -> sim` smoke

Headless smoke son marker:

```text
leader_smoke_ok {'task': 'LeIsaac-Franka-LiftCube-v0', 'num_envs': 1, 'joint_state_topic': '/joint_states', 'action_shape': (1, 9)}
```
## Live GUI follower launch

For the real `franka-leader -> Isaac Sim follower` GUI on the remote workstation, use:

```bash
~/furkan_workspace/leisaac/scripts/tutorials/run_franka_leader_gui.sh
```

Notes:
- This script sources `conda`, Isaac Sim, ROS 2 Humble, and the `5.4`-compatible `franka_ros2` workspace.
- It uses `--rendering_mode performance`.
- It intentionally does not pass `--enable_cameras`; that was making GUI startup much heavier on the remote desktop.
- Default task is `LeIsaac-Franka-BowlCubeZone-v0`. You can override it:

```bash
~/furkan_workspace/leisaac/scripts/tutorials/run_franka_leader_gui.sh LeIsaac-Franka-LiftCube-v0
```

## Gravity compensation mode

If the robot goes red when you try to guide it by hand in the state-only bringup mode, do not keep forcing it.

Official alternative:
- use the `gravity_compensation_example_controller`

Helpers added in this repo:

```bash
~/furkan_workspace/leisaac/scripts/tutorials/load_franka_54_gravity_comp.sh
```

To unload it:

```bash
~/furkan_workspace/leisaac/scripts/tutorials/unload_franka_54_gravity_comp.sh
```

Notes:
- only run this when the robot is on, FCI is active, and `franka_bringup` is already running
- keep the emergency stop ready
- do not force the robot by hand before the controller is active
