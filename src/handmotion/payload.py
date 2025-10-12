import math

from .config.config import config

from dataclasses import dataclass
from typing import List, Literal

Handedness = Literal["Left", "Right"]

WRIST = config.getint("LandmarkIndices", "WRIST")
THUMB_TIP = config.getint("LandmarkIndices", "THUMB_TIP")
INDEX_FINGER_TIP = config.getint("LandmarkIndices", "INDEX_FINGER_TIP")
MIDDLE_FINGER_TIP = config.getint("LandmarkIndices", "MIDDLE_FINGER_TIP")
RING_FINGER_TIP = config.getint("LandmarkIndices", "RING_FINGER_TIP")
PINKY_TIP = config.getint("LandmarkIndices", "PINKY_TIP")

CLICK_THRESHOLD = config.getfloat("MediaPipe", "CLICK_THRESHOLD")

@dataclass(kw_only=True)
class Landmark:
    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        pass

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

@dataclass
class NormalizedLandmark(Landmark):

    def __post_init__(self) -> None:
        super().__post_init__()
        # assert 0.0 <= self.x <= 1.0, f"x must be in [0,1]. Got {self.x} instead."
        # assert 0.0 <= self.y <= 1.0, f"y must be in [0,1]. Got {self.y} instead."

@dataclass
class Hand:
    in_frame: bool
    handedness: Handedness
    confidence: float
    landmarks: List[NormalizedLandmark]  # len == 21
    world_landmarks: List[Landmark]  # len == 21

    def __post_init__(self) -> None:
        assert len(self.landmarks) == 21, f"Hand Initialization: Hand must have exactly 21 landmarks. Got {len(self.landmarks)} instead."
        assert len(self.world_landmarks) == 21, f"Hand Initialization: Hand must have exactly 21 world landmarks. Got {len(self.world_landmarks)} instead."
        assert 0.0 <= self.confidence <= 1.0, f"Hand Initialization: Hand Confidence must be in [0,1]. Got {self.confidence} instead."

    def get_landmark(self, index: int) -> NormalizedLandmark:
        return self.landmarks[index]

    def get_world_landmark(self, index: int) -> Landmark:
        return self.world_landmarks[index]
    
    def calculate_xy_distance(self, lm1_idx: int, lm2_idx: int) -> float:
        lm1 = self.landmarks[lm1_idx]
        lm2 = self.landmarks[lm2_idx]
        return math.sqrt((lm1.x - lm2.x) ** 2 + 
                         (lm1.y - lm2.y) ** 2)
    
    def calculate_xyz_distance(self, lm1_idx: int, lm2_idx: int) -> float:
        lm1 = self.world_landmarks[lm1_idx]
        lm2 = self.world_landmarks[lm2_idx]
        return math.sqrt((lm1.x - lm2.x) ** 2 + 
                         (lm1.y - lm2.y) ** 2 + 
                         (lm1.z - lm2.z) ** 2)
    
    def is_touching(self, lm1_idx: int, lm2_idx: int, threshold: float = CLICK_THRESHOLD) -> bool:
        distance = self.calculate_xy_distance(lm1_idx, lm2_idx)
        return distance < threshold

@dataclass
class Meta:
    timestamp_ns: int
    width: int
    height: int
    fps_estimate: float

    def __post_init__(self) -> None:
        assert self.width > 0, f"Width must be positive. Got {self.width} instead."
        assert self.height > 0, f"Height must be positive. Got {self.height} instead."
        assert self.fps_estimate >= 0, f"FPS estimate must be positive. Got {self.fps_estimate} instead."

    def __str__(self):
        return (f"  MetaData: \n    Time Stamp (ns): {self.timestamp_ns}\n    Resolution: ({self.width}, {self.height})\n    FPS Estimate: {self.fps_estimate:.2f}")

@dataclass
class FramePayload:
    meta: Meta
    hands: List[Hand]

    def __str__(self) -> None:
        result = [f"Frame with {len(self.hands)} hands detected."]
        result.append(str(self.meta))

        for hand in self.hands:
            result.append(f"  {hand.handedness} Hand with confidence {hand.confidence:.2f} - In Frame: {hand.in_frame}")
            for i, lm in enumerate(hand.landmarks):
                result.append(f"    Landmark {i}: (x = {lm.x:.3f}, y = {lm.y:.3f}, z = {lm.z:.3f})")
        return "\n".join(result)