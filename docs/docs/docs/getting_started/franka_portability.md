# Franka Portability Checklist

Bu not, Franka real-to-sim hattını başka bir bilgisayara taşırken neyin repo içinde, neyin repo dışında olduğunu netleştirir.

## 1. Repo İçinde Taşınanlar

Bu repo ile birlikte taşınan ana parçalar:

- Franka sim task ve env config'leri
- `franka-leader`, `franka-keyboard`, `franka-spacemouse` device kodu
- Franka record/replay hattı
- fake-hardware ve smoke helper script'leri

Başka makinede aynı repo checkout'u ile bunlar gelir.

## 2. Repo Dışında Yeniden Kurulacaklar

Yeni makinede ayrıca hazır olmalı:

- Isaac Sim
- IsaacLab
- `env_isaacsim` veya eşdeğer conda env
- ROS 2
- `franka_ros2` workspace

Varsayılan beklenen klasörler:

- `ISAACSIM_ROOT=${ISAACSIM_ROOT:-$HOME/isaacsim}`
- `ISAACLAB_ROOT=${ISAACLAB_ROOT:-$HOME/IsaacLab}`
- `ROS_WS=${ROS_WS:-$HOME/franka_ros2_ws}`
- `CONDA_SH=${CONDA_SH:-$HOME/miniconda3/etc/profile.d/conda.sh}`

## 3. Hızlı Kontrol

Repo kökünde:

```bash
bash scripts/tutorials/check_franka_external_stack.sh
```

Bu script şu dış bağımlılıkları kontrol eder:

- conda init script
- Isaac Sim root
- Isaac Sim conda setup script
- IsaacLab launcher
- ROS setup
- `franka_ros2` workspace install setup
- gerekli scene asset'i

## 4. Override Edilebilen Env Var'lar

Kurulum yolları farklıysa helper script'ler şu değişkenleri kabul eder:

- `CONDA_SH`
- `CONDA_ENV_NAME`
- `ISAACSIM_ROOT`
- `ISAACLAB_ROOT`
- `ROS_DISTRO`
- `ROS_SETUP`
- `ROS_WS`

Örnek:

```bash
CONDA_SH=$HOME/mambaforge/etc/profile.d/conda.sh \
ISAACSIM_ROOT=/data/isaacsim \
ISAACLAB_ROOT=/data/IsaacLab \
ROS_WS=/data/franka_ros2_ws \
bash scripts/tutorials/check_franka_external_stack.sh
```

## 5. Bilinen Dış Patch

Bu projede yerel Isaac Sim kurulumu için ek bir uyumluluk shim'i gerekmişti:

- `$ISAACSIM_ROOT/__init__.py`

Yeni makinede AppLauncher tarafı çalışmazsa ilk bakılacak yer burasıdır.

## 6. Doğrulama Sırası

Taşıma sonrası önerilen sıra:

1. `check_franka_external_stack.sh`
2. `check_franka_phase6_smoke.sh`
3. `check_franka_real_to_sim_fake_smoke.sh`
4. sonra gerçek robot veya dataset recording denemeleri

## 7. Başarı Kriteri

Yeni makinede aşağıdakiler çalışıyorsa taşınabilirlik yeterli kabul edilir:

- Franka sim smoke
- fake-hardware real-to-sim smoke
- `franka-leader` ile follower env açılışı
