# Franka Real-to-Sim Dataset Roadmap

Amaç:

- Gerçek Franka robotunu elle hareket ettirerek `leader` olarak kullanmak
- Isaac Sim içindeki Franka'yı `follower` olarak sürmek
- Simülasyonda dataset toplamak

Notlar:

- Şu ana kadar yapılan işin büyük kısmı `sim Franka follower + task + record/replay` hattını ayağa kaldırdı.
- `keyboard teleop` ana hedef değildir ve şu an güvenilir kabul edilmemelidir.
- Bundan sonraki ana iş `real Franka leader adapter` katmanıdır.

## 0. Mevcut Durum

- [x] `LeIsaac-Franka-LiftCube-v0` task'i eklendi
- [x] Franka için sim task create/reset/step smoke test geçti
- [x] Franka için küçük HDF5 dataset record smoke geçti
- [x] Franka için `replay --replay_mode action` smoke geçti
- [ ] Franka keyboard teleop güvenilir şekilde doğrulandı
- [x] Gerçek Franka'dan veri okuyan leader katmanı mevcut

## 1. Hedef Arayüzü Netleştirme

- [x] Gerçek Franka bağlantı yöntemini netleştir
- [x] Kullanılan stack'i netleştir: `franka_ros2`, `libfranka`, vendor bridge, başka bir katman
- [ ] Okunabilir state'leri netleştir:
- [x] `joint positions`
- [ ] `joint velocities`
- [x] `gripper width/state`
- [ ] `end-effector pose`
- [ ] Gerçek Franka'nın leader modunda güvenli kullanım koşullarını netleştir
- [x] Teleop sırasında hangi tarafın motion authority olduğunu netleştir

Teslim kriteri:

- Gerçek Franka'dan hangi topic/API üzerinden hangi veriyi okuyacağımız net olmalı.

Seçilen ilk faz:

- Bridge: `franka_ros2`
- Veri kaynağı: `joint_states`
- İlk veri modeli: `joint positions + gripper state`
- İlk follower komut modeli: `joint-space mirroring`

## 2. SO101 Leader Zincirini Referans Olarak Ayrıştırma

- [x] `so101_leader.py` davranışını belgeleyip ayır
- [x] Device -> action preprocess -> env zincirini çıkar
- [x] SO101'e özel kalan kısımları listele
- [x] Franka için yeniden kullanılacak generic parçaları listele

Referans dosyalar:

- [so101_leader.py](/home/nvidia/leisaac/source/leisaac/leisaac/devices/lerobot/so101_leader.py)
- [device_base.py](/home/nvidia/leisaac/source/leisaac/leisaac/devices/device_base.py)
- [action_process.py](/home/nvidia/leisaac/source/leisaac/leisaac/devices/action_process.py)

Teslim kriteri:

- Franka leader adapter için net write planı çıkmış olmalı.

## 3. Franka Leader Veri Modeli

- [x] Franka leader için kullanılacak observation/action temsilini seç
- [x] İlk iterasyon için karar ver:
- [x] `joint-space mirroring`
- [ ] veya `ee-pose mirroring`
- [x] Gripper state semantiğini netleştir
- [x] Leader veri modelini sabit bir adapter arayüzüne dök

Öneri:

- İlk iterasyon: `joint positions + gripper`
- İkinci iterasyon: `ee pose + gripper`

Teslim kriteri:

- Franka leader'dan gelen veri ile sim Franka'ya verilecek komut formatı birebir tanımlı olmalı.

## 4. Franka Leader Device İskeleti

- [x] Yeni device modülü oluştur
- [x] `FrankaLeader` sınıfı ekle
- [x] Cihaz tipi ekle: ör. `franka-leader`
- [x] Başlatma/bağlantı kontrolü ekle
- [x] `advance()` içinde gerçek Franka state okumasını bağla
- [x] `reset()` davranışını tanımla
- [x] Gerekli callback davranışlarını tanımla

Olası dosyalar:

- [devices](/home/nvidia/leisaac/source/leisaac/leisaac/devices)
- [teleop_se3_agent.py](/home/nvidia/leisaac/scripts/environments/teleoperation/teleop_se3_agent.py)

Teslim kriteri:

- Sim env tarafına gerçek Franka state'i gönderen ilk leader device ayağa kalkmalı.

## 5. Franka Action Köprüsü

- [x] `action_process.py` içinde `franka-leader` branch'i ekle
- [x] Gelen leader state'ini sim Franka action space'ine çevir
- [x] Gerekirse joint order mapping ekle
- [x] Gerekirse gripper normalization ekle
- [x] İlk çalışan mod için minimal action köprüsü kur

Seçenekler:

- [ ] `joint state -> joint action`
- [ ] `joint state -> ee pose -> IK action`
- [ ] `ee pose -> IK action`

Teslim kriteri:

- Gerçek Franka hareketi sim Franka üzerinde gözle görünür biçimde takip edilmeli.

## 6. Real-to-Sim Teleop Smoke

- [x] Remote PC üzerinde Wi-Fi + Franka Ethernet çift ağ yapısını kur
- [x] Remote PC'de `enp4s0 -> 172.16.0.1/24` yapılandırmasını doğrula
- [x] Gerçek Franka `172.16.0.2` ping erişimini doğrula
- [ ] Gerçek Franka bağlıyken sim Franka'yı boş sahnede sür
- [x] Tek env smoke test yaz
- [ ] Delay / jitter gözlemi yap
- [ ] Gripper açık/kapalı testi yap
- [ ] Reset sonrası state senkronunu doğrula

Teslim kriteri:

- Gerçek Franka leader hareketi sim Franka follower üzerinde stabil görünmeli.

## 7. Dataset Recording Smoke

- [x] `franka-leader` ile `LiftCube` task üzerinde kısa kayıt al
- [x] HDF5 dosyası oluştuğunu doğrula
- [x] Episode sayısını doğrula
- [x] `replay --replay_mode action` ile tekrar oynat
- [x] Observation/action şemasını doğrula

Teslim kriteri:

- Gerçek Franka hareketiyle üretilen ilk sim dataset kaydı ve replay'i başarılı olmalı.

## 8. Task Genişletme

- [ ] `LiftCube` sonrası ikinci Franka task seç
- [ ] Gerekirse `StackCube` task'ini ekle
- [ ] Leader ile ikinci task smoke yap
- [ ] Task success / reset mantığını doğrula

Teslim kriteri:

- En az iki Franka task'i real-to-sim veri toplama için kullanılabilir olmalı.

## 9. Recorder ve Export Sertleştirme

- [ ] Uzun kayıt testi yap
- [ ] Episode boundary'leri doğrula
- [ ] Başarısız episode davranışını doğrula
- [ ] LeRobot export gerekiyorsa Franka dataset dönüşümünü doğrula
- [ ] Naming / schema sabitle

Teslim kriteri:

- Dataset formatı eğitim hattına verilebilir durumda olmalı.

## 10. Interactive Teleop Sorunları

- [ ] Keyboard teleop neden güvenilir değil onu ayrı issue olarak kapat
- [ ] Isaac pencere focus / input / app mode problemlerini izole et
- [ ] Bu sorunu ana hedeften bağımsız tut

Not:

- Keyboard teleop düzelse de ana hedef için kritik değil.
- Ana öncelik `real Franka leader -> sim Franka follower`.

## 11. Güvenlik ve Operasyon

- [ ] Gerçek Franka kullanımı için hız limitleri tanımla
- [ ] Workspace limitleri tanımla
- [ ] E-stop prosedürünü yaz
- [ ] Sim ve real senkron bozulduğunda fallback davranışını tanımla

Teslim kriteri:

- Gerçek donanımla tekrar edilebilir ve güvenli çalışma prosedürü oluşmalı.

## 12. Taşınabilirlik

- [x] Helper script'lerde makineye gömülü path'leri env var tabanlı hale getir
- [x] Dış bağımlılıkları tek script ile kontrol et
- [x] Yeni makine için taşıma checklist'i yaz
- [x] Yeni makinada `check_franka_external_stack.sh` çalıştırıp doğrula

Teslim kriteri:

- Repo checkout'u farklı kullanıcı/path altında minimum env override ile ayağa kalkmalı.

## Kısa Öncelik Sırası

- [x] 1. Gerçek Franka arayüzünü netleştir
- [x] 2. `FrankaLeader` device iskeletini çıkar
- [x] 3. İlk real-to-sim smoke'u çalıştır
- [x] 4. Dataset record/replay doğrula
- [ ] 5. Sonra task genişlet

## Şu An Bir Sonraki Somut Adım

- [x] Gerçek Franka hangi API/topic/driver ile okunuyor onu kod seviyesinde netleştir
- [x] Buna göre `FrankaLeader` için ilk adapter dosyasını aç
- [x] `franka_ros2` çalışan robot üzerinde `/joint_states` yayınını doğrula
- [x] `--teleop_device franka-leader` ile ilk sim follower smoke'unu çalıştır

## Son Durum Notu

- Aynı makinede `franka_ros2` workspace hazır: varsayılan `$HOME/franka_ros2_ws`
- Fake hardware ile `/joint_states` doğrulandı
- Bu makinada `fr3_*` joint isimleri yayınlanıyor; `FrankaLeader` artık `panda_*` ve `fr3_*` ailelerini destekliyor
- Uzak `lira` makinesinde `env_isaacsim + ~/IsaacLab + ~/franka_ros2_ws` ile fake `leader -> sim follower` smoke geçti
- `pygame` ve `serial` artık Franka hattı için zorunlu import değil; gamepad/SO101/LeKiwi donanım bağımlılıkları opsiyonel
- Fake smoke helper artık ROS CLI topic introspection yerine doğrudan `FrankaLeader` subscriber ile doğrulama yapıyor
- Uzak makinede `git-lfs` kuruldu ve `table_with_cube/scene.usd` gerçek USD olarak çekildi
- Faz 7 local makinede `record -> replay(action)` olarak doğrulandı
- Uzak makinede Faz 7 de `record -> replay(action)` olarak doğrulandı
- Uzak makinedeki asıl blocker kaynak baskısı değil, `Isaac Sim 4.5` ile `IsaacLab v2.3.2` uyumsuzluğuydu
- Uzak makinede `~/IsaacLab` yerelde çalışan `19b24c780ea` (`v2.1.1-4`) commit'ine hizalandı
- `replay.py` artık `simulation_app.close()` çağırıyor ve completion marker'ını `flush=True` ile yazarak wrapper log doğrulamasını güvenilir hale getiriyor
- Tek komutluk smoke helper:
  - [check_franka_real_to_sim_fake_smoke.sh](/home/nvidia/leisaac/scripts/tutorials/check_franka_real_to_sim_fake_smoke.sh)
- Tek komutluk record/replay helper:
  - [check_franka_real_to_sim_record_replay_fake_smoke.sh](/home/nvidia/leisaac/scripts/tutorials/check_franka_real_to_sim_record_replay_fake_smoke.sh)
- Taşınabilir dış-bağımlılık kontrol helper'ı:
  - [check_franka_external_stack.sh](/home/nvidia/leisaac/scripts/tutorials/check_franka_external_stack.sh)
- Taşıma checklist'i:
  - [franka_portability.md](/home/nvidia/leisaac/docs/docs/docs/getting_started/franka_portability.md)
- Operasyon notu:
  - [franka_real_to_sim_smoke.md](/home/nvidia/leisaac/docs/docs/docs/getting_started/franka_real_to_sim_smoke.md)
- Ağ ve robot erişim notu:
  - [franka_setup.md](/home/nvidia/leisaac/docs/docs/docs/getting_started/franka_setup.md)
- Uzak `lira` makinesinde Wi-Fi (`wlp3s0`) ve Franka Ethernet (`enp4s0`) aynı anda çalışacak şekilde yapılandırma doğrulandı
- `Wired connection 1` artık `172.16.0.1/24`, `never-default=yes`, `ipv6.method=ignore` ile Franka ağı için kalıcı profile sahip
- Gerçek Franka robotu `172.16.0.2` olarak `ping -I enp4s0` ile doğrulandı
- `franka_ros2` gerçek donanım bringup denemesi yapıldı ancak şu an blocker `FCI refused`
- Sonraki fiziksel adım Desk üzerinde `Activate FCI` ve FCI feature kontrolü
