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

Bu, şu an iki şeyden birinin eksik olduğunu gösterir:

1. Robotta FCI feature yüklü değil
2. Desk içinde FCI mode aktif değil

Doğrulanan durum:

- Robot web arayüzü erişilebilir:
  - `https://172.16.0.2/desk/`
- Ağ erişimi tamam:
  - `ping -I enp4s0 172.16.0.2` başarılı
- FCI tarafı reddediliyor:
  - `ros2 launch franka_bringup franka.launch.py ...` başarısız

## Desk Tarafında Yapılması Gerekenler

Desk üzerinde:

1. Brakeleri çöz
2. Robotu execution-ready duruma getir
3. Menüden `Activate FCI` seç
4. Gerekirse çıkan onay penceresini açık bırak

Ek kontrol:

- `Settings -> System -> Installed Features` altında FCI feature kurulu olmalı

## FCI Açıldıktan Sonra Doğrulama

Remote PC üzerinde:

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

Ayrı terminalde:

```bash
source /opt/ros/humble/setup.bash
source ~/franka_ros2_ws/install/setup.bash

ros2 topic list | grep joint_states
ros2 topic echo /joint_states --once
```
