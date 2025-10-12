from ..config.config import config
from .base import BaseInterface
from ..payload import FramePayload

__all__ = ["config", "BaseInterface", "FramePayload"]

def get_hand_preference(interface: str) -> str:
    return config.get(interface, "HAND_PREFERENCE")

def get_click_threshold() -> float:
    return config.getfloat("MediaPipe", "CLICK_THRESHOLD")

def get_thumb_tip_index() -> int:
    return config.getint("LandmarkIndices", "THUMB_TIP")

def get_index_finger_tip_index() -> int:
    return config.getint("LandmarkIndices", "INDEX_FINGER_TIP")
    
def get_middle_finger_tip_index() -> int:
    return config.getint("LandmarkIndices", "MIDDLE_FINGER_TIP")

def get_ring_finger_tip_index() -> int:
    return config.getint("LandmarkIndices", "RING_FINGER_TIP")

def get_pinky_tip_index() -> int:
    return config.getint("LandmarkIndices", "PINKY_TIP")