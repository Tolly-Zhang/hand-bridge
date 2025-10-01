from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal

Handedness = Literal["Left", "Right"]

WRIST = 0
THUMB_TIP = 4
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_TIP = 12
RING_FINGER_TIP = 16
PINKY_TIP = 20

@dataclass
class Landmark:
    x_norm: float  # [0,1]
    y_norm: float  # [0,1]
    z_norm: float  # MediaPipe relative depth (optional use)

    def __post_init__(self) -> None:
        assert 0.0 <= self.x_norm <= 1.0, f"x_norm must be in [0,1]. Got {self.x_norm} instead."
        assert 0.0 <= self.y_norm <= 1.0, f"y_norm must be in [0,1]. Got {self.y_norm} instead."

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x_norm, self.y_norm, self.z_norm)

@dataclass
class Hand:
    handedness: Handedness
    confidence: float
    landmarks: List[Landmark]  # len == 21
    world_landmarks: List[Landmark]  # len == 21

    def __post_init__(self) -> None:
        assert len(self.landmarks) == 21, f"Hand must have exactly 21 landmarks. Got {len(self.landmarks)} instead."
        assert len(self.world_landmarks) == 21, f"Hand must have exactly 21 world landmarks. Got {len(self.world_landmarks)} instead."
        assert 0.0 <= self.confidence <= 1.0, f"Confidence must be in [0,1]. Got {self.confidence} instead."

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

@dataclass
class FramePayload:
    meta: Meta
    hands: List[Hand]

    def print_summary(self) -> None:
        print(f"Frame at {self.meta.timestamp_ns} ns: {len(self.hands)} hands detected.")
        for hand in self.hands:
            print(f"  Hand {hand.handedness} with confidence {hand.confidence:.2f}")
