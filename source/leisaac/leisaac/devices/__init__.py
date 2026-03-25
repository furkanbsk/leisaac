from .device_base import DeviceBase
from .franka import FrankaKeyboard, FrankaLeader, FrankaSpaceMouse
from .keyboard import SO101Keyboard

try:
    from .gamepad import SO101Gamepad
except ModuleNotFoundError:
    SO101Gamepad = None

try:
    from .lekiwi import LeKiwiGamepad, LeKiwiKeyboard, LeKiwiLeader
except ModuleNotFoundError:
    LeKiwiGamepad = None
    LeKiwiKeyboard = None
    LeKiwiLeader = None

try:
    from .lerobot import BiSO101Leader, SO101Leader
except ModuleNotFoundError:
    BiSO101Leader = None
    SO101Leader = None
